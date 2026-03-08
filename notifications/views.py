"""
Views for notifications app.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Notification, Newsletter
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """Get user notifications."""
    notifications = Notification.objects.filter(user=request.user)
    
    data = [{
        'id': n.id,
        'type': n.type,
        'title': n.title,
        'message': n.message,
        'link': n.link,
        'is_read': n.is_read,
        'created_at': n.created_at,
    } for n in notifications]
    
    return Response({
        'notifications': data,
        'unread_count': notifications.filter(is_read=False).count()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark notification as read."""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    
    return Response({'message': 'Notification marked as read.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe_newsletter(request):
    """Subscribe to newsletter."""
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    newsletter, created = Newsletter.objects.get_or_create(
        email=email,
        defaults={'is_active': True}
    )
    
    if created:
        # Send confirmation email
        try:
            subject = 'Newsletter Subscription Confirmed'
            
            # Plain text version
            text_content = f'''Thank you for subscribing to the Fleeto newsletter!

You will now receive updates, exclusive offers, and the latest news at {email}.

If you wish to unsubscribe at any time, you can do so from any of our emails.

Best regards,
The Fleeto Team'''
            
            # HTML version
            html_content = f'''
                <h1>Welcome to the Fleeto Newsletter! 📬</h1>
                <p>Thank you for subscribing to our newsletter!</p>
                <p>You'll now receive:</p>
                <ul style="line-height: 1.8;">
                    <li>🎁 Exclusive offers and discounts</li>
                    <li>🆕 New product announcements</li>
                    <li>📰 Latest news and updates</li>
                    <li>💡 Tips and recommendations</li>
                </ul>
                
                <div class="info-box">
                    <p style="margin: 0;"><strong>Subscribed Email:</strong> {email}</p>
                </div>
                
                <p style="font-size: 14px; color: #999;">You can unsubscribe at any time by clicking the unsubscribe link in any of our emails.</p>
            '''
            
            logger.info("[email] Sending newsletter confirmation\\nFrom: %s\\nTo: %s\\nSubject: %s",
                        settings.DEFAULT_FROM_EMAIL, email, subject)
            
            from users.email_utils import send_fleeto_email
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[email]
            )
            logger.info("[email] Newsletter confirmation queued", extra={'to': email})
        except Exception:
            logger.exception("[email] Newsletter confirmation failed", extra={'to': email})
        return Response({
            'message': 'Successfully subscribed to newsletter!'
        }, status=status.HTTP_201_CREATED)
    
    if not newsletter.is_active:
        newsletter.is_active = True
        newsletter.save()
        return Response({
            'message': 'Successfully re-subscribed to newsletter!'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'message': 'You are already subscribed.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe_newsletter(request):
    """Unsubscribe from newsletter."""
    email = request.data.get('email')
    
    try:
        newsletter = Newsletter.objects.get(email=email)
        newsletter.is_active = False
        newsletter.save()
        return Response({
            'message': 'Successfully unsubscribed from newsletter.'
        }, status=status.HTTP_200_OK)
    except Newsletter.DoesNotExist:
        return Response({
            'error': 'Email not found in our newsletter list.'
        }, status=status.HTTP_404_NOT_FOUND)


