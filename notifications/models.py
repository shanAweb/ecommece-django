"""
Models for notifications app.
"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """User notification model."""
    
    TYPE_CHOICES = [
        ('order', 'Order Update'),
        ('payment', 'Payment'),
        ('shipping', 'Shipping'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class Newsletter(models.Model):
    """Newsletter subscription model."""
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'newsletter_subscriptions'
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email


class NewsletterCampaign(models.Model):
    """Newsletter campaign model for admin to send newsletters."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    ]
    
    subject = models.CharField(max_length=255, help_text="Email subject line")
    content = models.TextField(
        help_text="Newsletter content - you can use simple HTML tags like <h1>, <p>, <ul>, <li>, <a>, <strong>, etc."
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_newsletters'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the newsletter was sent")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    recipient_count = models.IntegerField(default=0, help_text="Number of recipients")
    
    class Meta:
        db_table = 'newsletter_campaigns'
        verbose_name = 'Newsletter Campaign'
        verbose_name_plural = 'Newsletter Campaigns'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"
    
    def get_plain_text(self):
        """Convert HTML content to plain text."""
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', self.content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


