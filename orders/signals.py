"""
Signal handlers for orders app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Order
from users.email_utils import send_fleeto_email
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """Send email notifications when order is created or updated."""
    
    if created:
        # Send order confirmation email
        subject = f'Order Confirmation - {instance.order_number}'
        
        # Plain text version
        text_content = f'''
Hi {instance.shipping_full_name},

Thank you for your order! Your order has been confirmed.

Order Number: {instance.order_number}
Order Total: ${instance.total_amount}

We'll send you another email when your order ships.

View your order: {settings.SITE_URL}/orders/{instance.order_number}/

Thank you for shopping with Fleeto!

Best regards,
The Fleeto Team
        '''
        
        # HTML version
        html_content = f'''
            <h1>Order Confirmation 🎉</h1>
            <p>Hi <strong>{instance.shipping_full_name}</strong>,</p>
            <p>Thank you for your order! We're excited to get your items to you.</p>
            
            <div class="info-box">
                <p style="margin: 0 0 10px 0;"><strong>Order Number:</strong> {instance.order_number}</p>
                <p style="margin: 0;"><strong>Order Total:</strong> <span style="color: #667eea; font-size: 20px; font-weight: bold;">${instance.total_amount}</span></p>
            </div>
            
            <p>We'll send you another email with tracking information once your order ships.</p>
            
            <p style="text-align: center;">
                <a href="{settings.SITE_URL}/orders/{instance.order_number}/" class="button">
                    View Order Details
                </a>
            </p>
            
            <p>Thank you for shopping with Fleeto! 🛍️</p>
        '''
        
        try:
            logger.info("[email] Sending order confirmation\\nFrom: %s\\nTo: %s\\nSubject: %s",
                        settings.DEFAULT_FROM_EMAIL, instance.shipping_email, subject)
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[instance.shipping_email]
            )
            logger.info("[email] Order confirmation queued", extra={'order': instance.order_number})
        except Exception as e:
            logger.exception("[email] Order confirmation failed", extra={'order': instance.order_number})
    
    elif instance.status == 'shipped' and instance.tracking_number:
        # Send shipping notification
        subject = f'Your Order Has Shipped - {instance.order_number}'
        
        # Plain text version
        text_content = f'''
Hi {instance.shipping_full_name},

Great news! Your order has been shipped.

Order Number: {instance.order_number}
Tracking Number: {instance.tracking_number}
Carrier: {instance.carrier}

You can track your package at: {settings.SITE_URL}/orders/{instance.order_number}/track/

Thank you for shopping with Fleeto!

Best regards,
The Fleeto Team
        '''
        
        # HTML version
        html_content = f'''
            <h1>Your Order Has Shipped! 📦</h1>
            <p>Hi <strong>{instance.shipping_full_name}</strong>,</p>
            <p>Great news! Your order is on its way to you.</p>
            
            <div class="info-box">
                <p style="margin: 0 0 10px 0;"><strong>Order Number:</strong> {instance.order_number}</p>
                <p style="margin: 0 0 10px 0;"><strong>Tracking Number:</strong> {instance.tracking_number}</p>
                <p style="margin: 0;"><strong>Carrier:</strong> {instance.carrier}</p>
            </div>
            
            <p style="text-align: center;">
                <a href="{settings.SITE_URL}/orders/{instance.order_number}/track/" class="button">
                    Track Your Package
                </a>
            </p>
            
            <p>Your order should arrive soon. Thank you for shopping with Fleeto! 🚚</p>
        '''
        
        try:
            logger.info("[email] Sending shipped notification\\nFrom: %s\\nTo: %s\\nSubject: %s",
                        settings.DEFAULT_FROM_EMAIL, instance.shipping_email, subject)
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[instance.shipping_email]
            )
        except Exception as e:
            logger.exception("[email] Shipped notification failed", extra={'order': instance.order_number})
    
    elif instance.status == 'delivered':
        # Send delivery confirmation
        subject = f'Your Order Has Been Delivered - {instance.order_number}'
        
        # Plain text version
        text_content = f'''
Hi {instance.shipping_full_name},

Your order has been delivered!

Order Number: {instance.order_number}

We hope you love your purchase! If you have any questions or concerns, please don't hesitate to contact us.

Leave a review: {settings.SITE_URL}/orders/{instance.order_number}/review/

Thank you for shopping with Fleeto!

Best regards,
The Fleeto Team
        '''
        
        # HTML version
        html_content = f'''
            <h1>Your Order Has Been Delivered! ✅</h1>
            <p>Hi <strong>{instance.shipping_full_name}</strong>,</p>
            <p>Great news! Your order has been successfully delivered.</p>
            
            <div class="info-box">
                <p style="margin: 0;"><strong>Order Number:</strong> {instance.order_number}</p>
            </div>
            
            <p>We hope you love your purchase! Your feedback helps us improve and helps other customers make informed decisions.</p>
            
            <p style="text-align: center;">
                <a href="{settings.SITE_URL}/orders/{instance.order_number}/review/" class="button">
                    Leave a Review ⭐
                </a>
            </p>
            
            <p>If you have any questions or concerns about your order, please don't hesitate to contact us.</p>
            
            <p>Thank you for shopping with Fleeto! 💚</p>
        '''
        
        try:
            logger.info("[email] Sending delivery confirmation\\nFrom: %s\\nTo: %s\\nSubject: %s",
                        settings.DEFAULT_FROM_EMAIL, instance.shipping_email, subject)
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[instance.shipping_email]
            )
        except Exception as e:
            logger.exception("[email] Delivery confirmation failed", extra={'order': instance.order_number})



@receiver(pre_save, sender=Order)
def send_order_status_change(sender, instance, **kwargs):
    """Notify user when status changes (generic)."""
    if not instance.pk:
        return
    try:
        prev = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return
    if prev.status != instance.status:
        subject = f"Order {instance.order_number} Status Updated"
        
        # Plain text version
        text_content = f"""Hi {instance.shipping_full_name},

Your order status has been updated.

Order Number: {instance.order_number}
Previous Status: {prev.get_status_display()}
New Status: {instance.get_status_display()}

View your order: {settings.SITE_URL}/orders/{instance.order_number}/

Best regards,
The Fleeto Team"""
        
        # HTML version
        html_content = f'''
            <h1>Order Status Update 📋</h1>
            <p>Hi <strong>{instance.shipping_full_name}</strong>,</p>
            <p>Your order status has been updated.</p>
            
            <div class="info-box">
                <p style="margin: 0 0 10px 0;"><strong>Order Number:</strong> {instance.order_number}</p>
                <p style="margin: 0 0 10px 0;"><strong>Previous Status:</strong> {prev.get_status_display()}</p>
                <p style="margin: 0;"><strong>New Status:</strong> <span style="color: #667eea; font-weight: bold;">{instance.get_status_display()}</span></p>
            </div>
            
            <p style="text-align: center;">
                <a href="{settings.SITE_URL}/orders/{instance.order_number}/" class="button">
                    View Order Details
                </a>
            </p>
        '''
        
        try:
            logger.info("[email] Sending order status change\\nFrom: %s\\nTo: %s\\nSubject: %s",
                        settings.DEFAULT_FROM_EMAIL, instance.shipping_email, subject)
            send_fleeto_email(
                subject=subject,
                text_content=text_content,
                html_content=html_content,
                recipient_list=[instance.shipping_email]
            )
        except Exception:
            logger.exception("[email] Order status change email failed", extra={'order': instance.order_number})
