"""
Views for users app.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import uuid
import logging

from .models import User, UserSession, Address, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, AddressSerializer, UserSessionSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .utils import get_device_info, get_client_ip
from .email_utils import send_fleeto_email


logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create new user and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send email verification
        verify_url = f"{settings.SITE_URL}/verify-email/{user.email_verification_token}/"
        try:
            subject = 'Verify your email address'
            
            # Plain text version
            text_content = f"""Hi {user.get_full_name()},

Please verify your email by clicking the link below:
{verify_url}

Best regards,
The Fleeto Team"""
            
            # HTML version
            html_content = f'''
                <h1>Verify Your Email Address</h1>
                <p>Hi <strong>{user.get_full_name()}</strong>,</p>
                <p>Thank you for registering with Fleeto! To complete your registration, please verify your email address.</p>
                
                <p style="text-align: center;">
                    <a href="{verify_url}" class="button">
                        Verify Email Address
                    </a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verify_url}</p>
            '''
            
            logger.info("[email] Sending verification email\nFrom: %s\nTo: %s\nSubject: %s",
                        settings.DEFAULT_FROM_EMAIL, user.email, subject)
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[user.email]
            )
            logger.info("[email] Verification email queued", extra={'to': user.email})
        except Exception:
            logger.exception("[email] Verification email failed", extra={'to': user.email})

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Create session
        device_info = get_device_info(request)
        UserSession.objects.create(
            user=user,
            session_key=str(uuid.uuid4()),
            refresh_token=str(refresh),
            ip_address=get_client_ip(request),
            **device_info
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful! Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with session tracking."""
    
    def post(self, request, *args, **kwargs):
        """Login user and create session."""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            if not user.is_email_verified:
                return Response({'error': 'Please verify your email before logging in.'}, status=status.HTTP_403_FORBIDDEN)
            refresh_token = response.data.get('refresh')
            
            # Create or update session
            device_info = get_device_info(request)
            session_key = str(uuid.uuid4())
            
            UserSession.objects.create(
                user=user,
                session_key=session_key,
                refresh_token=refresh_token,
                ip_address=get_client_ip(request),
                **device_info
            )
            
            # Add session key to response
            response.data['session_key'] = session_key
            response.data['user'] = UserSerializer(user).data
        
        return response


class LogoutView(APIView):
    """Logout and invalidate session."""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        """Logout current session."""
        try:
            refresh_token = request.data.get('refresh_token')
            
            if refresh_token:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                # Deactivate session
                UserSession.objects.filter(
                    user=request.user,
                    refresh_token=refresh_token
                ).update(is_active=False)
            
            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAllDevicesView(APIView):
    """Logout from all devices."""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        """Logout from all sessions."""
        try:
            # Deactivate all user sessions
            UserSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            return Response({
                'message': 'Successfully logged out from all devices.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile."""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer
    
    def get_object(self):
        """Return current user."""
        return self.request.user


class ChangePasswordView(APIView):
    """Change user password."""
    
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        """Change password."""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Deactivate all sessions except current
            UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
            
            return Response({
                'message': 'Password changed successfully. Please login again.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    """List and create user addresses."""
    
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        """Return addresses for current user."""
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create address for current user."""
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete user address."""
    
    serializer_class = AddressSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        """Return addresses for current user."""
        return Address.objects.filter(user=self.request.user)


class UserSessionListView(generics.ListAPIView):
    """List all user sessions."""
    
    serializer_class = UserSessionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        """Return sessions for current user."""
        return UserSession.objects.filter(user=self.request.user, is_active=True)


class PasswordResetRequestView(APIView):
    """Request password reset."""
    
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        """Send password reset email."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Create reset token
            expires_at = timezone.now() + timedelta(hours=24)
            reset_token = PasswordResetToken.objects.create(
                user=user,
                expires_at=expires_at
            )
            
            # Send email
            reset_url = f"{settings.SITE_URL}/reset-password/{reset_token.token}/"
            subject = 'Password Reset Request'
            
            # Plain text version
            text_content = f'''Hi {user.get_full_name()},

You requested a password reset. Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
The Fleeto Team'''
            
            # HTML version
            html_content = f'''
                <h1>Password Reset Request</h1>
                <p>Hi <strong>{user.get_full_name()}</strong>,</p>
                <p>We received a request to reset your password for your Fleeto account.</p>
                
                <div class="info-box">
                    <p style="margin: 0;"><strong>⏰ Important:</strong> This link will expire in 24 hours.</p>
                </div>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">
                        Reset Password
                    </a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                
                <p style="color: #999; font-size: 14px;">If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
            '''
            
            logger.info("[email] Sending password reset email\nFrom: %s\nTo: %s\nSubject: %s",
                        settings.DEFAULT_FROM_EMAIL, user.email, subject)
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[user.email]
            )
            logger.info("[email] Password reset email queued", extra={'to': user.email})
            
            return Response({
                'message': 'Password reset email sent. Please check your inbox.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Confirm password reset."""
    
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        """Reset password with token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token)
                
                if not reset_token.is_valid():
                    return Response({
                        'error': 'Invalid or expired token.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Reset password
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Mark token as used
                reset_token.is_used = True
                reset_token.save()
                
                # Deactivate all sessions
                UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
                
                return Response({
                    'message': 'Password reset successful. Please login with your new password.'
                }, status=status.HTTP_200_OK)
                
            except PasswordResetToken.DoesNotExist:
                return Response({
                    'error': 'Invalid token.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request, token):
    """Verify user email."""
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.save()
        
        return Response({
            'message': 'Email verified successfully!'
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid verification token.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contact_form(request):
    """Handle contact form submissions."""
    try:
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        email = request.data.get('email', '')
        subject = request.data.get('subject', '')
        message = request.data.get('message', '')
        
        # Validate required fields
        if not all([first_name, last_name, email, subject, message]):
            return Response({
                'error': 'All fields are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get subject label
        subject_labels = {
            'general': 'General Inquiry',
            'order': 'Order Status',
            'product': 'Product Question',
            'return': 'Returns & Exchanges',
            'feedback': 'Feedback',
            'other': 'Other'
        }
        subject_label = subject_labels.get(subject, 'Contact Form')
        
        # Prepare email content
        full_name = f"{first_name} {last_name}"
        email_subject = f"[Fleeto] New Contact Form: {subject_label}"
        email_message = f"""
New contact form submission from Fleeto website:

Name: {full_name}
Email: {email}
Subject: {subject_label}

Message:
{message}

---
This message was sent via the contact form on {settings.SITE_URL}/contact/
        """
        
        # Log email details
        logger.info("[CONTACT FORM] New submission")
        logger.info("[email] Sending contact form notification to admin")
        
        # Send plain text email to admin (admin doesn't need fancy HTML)
        from django.core.mail import send_mail
        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Send to admin email
            fail_silently=False,
        )
        logger.info("[email] Contact form notification sent successfully to admin")
        
        # Send confirmation email to customer with HTML template
        customer_subject = f"Thank you for contacting Fleeto"
        
        # Plain text version
        customer_text = f"""
Hi {full_name},

Thank you for reaching out to us! We've received your message and will get back to you within 24-48 hours.

Your message:
Subject: {subject_label}
{message}

Best regards,
The Fleeto Team
{settings.SITE_URL}
        """
        
        # HTML version
        customer_html = f'''
            <h1>Thank You for Contacting Us! 💬</h1>
            <p>Hi <strong>{full_name}</strong>,</p>
            <p>We've received your message and appreciate you taking the time to reach out to us.</p>
            
            <div class="info-box">
                <p style="margin: 0 0 10px 0;"><strong>Response Time:</strong> We'll get back to you within 24-48 hours.</p>
                <p style="margin: 0;"><strong>Subject:</strong> {subject_label}</p>
            </div>
            
            <p><strong>Your Message:</strong></p>
            <p style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; font-style: italic;">
                {message.replace(chr(10), "<br>")}  
            </p>
            
            <p>If you have any additional questions in the meantime, feel free to reply to this email.</p>
        '''
        
        logger.info("[email] Sending confirmation email to customer: %s", email)
        
        send_fleeto_email(
            subject=customer_subject,
            text_content=customer_text,
            html_content=customer_html,
            recipient_list=[email]
        )
        logger.info("[email] Confirmation email sent successfully to customer")
        
        return Response({
            'message': 'Thank you for contacting us! We will respond within 24-48 hours.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"[CONTACT FORM] Error processing contact form: {str(e)}")
        return Response({
            'error': 'Failed to send message. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


