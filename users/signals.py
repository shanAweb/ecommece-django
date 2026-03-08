"""
Signal handlers for users app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User
from .email_utils import send_fleeto_email
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """Send welcome email to new users."""
    if created and not instance.is_superuser:
        subject = f'Welcome to {settings.SITE_NAME}!'
        
        # Plain text version
        text_content = f'''
Hi {instance.get_full_name()},

Welcome to {settings.SITE_NAME}! We're excited to have you on board.

Please verify your email address by clicking the link below:
{settings.SITE_URL}/verify-email/{instance.email_verification_token}/

Happy shopping!

Best regards,
The Fleeto Team
        '''
        
        # HTML version
        html_content = f'''
            <h1>Welcome to Fleeto! 🎉</h1>
            <p>Hi <strong>{instance.get_full_name()}</strong>,</p>
            <p>We're thrilled to have you join the Fleeto community! Your account has been successfully created.</p>
            
            <div class="info-box">
                <p style="margin: 0;"><strong>Next Step:</strong> Verify your email address to unlock all features.</p>
            </div>
            
            <p style="text-align: center;">
                <a href="{settings.SITE_URL}/verify-email/{instance.email_verification_token}/" class="button">
                    Verify Email Address
                </a>
            </p>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #667eea;">{settings.SITE_URL}/verify-email/{instance.email_verification_token}/</p>
            
            <p>Happy shopping! 🛍️</p>
        '''
        
        try:
            logger.info("[email] Sending welcome email to %s", instance.email)
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[instance.email]
            )
            logger.info("[email] Welcome email sent successfully")
        except Exception as e:
            logger.exception(f"Failed to send welcome email: {e}")


