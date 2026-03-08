"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import Notification, Newsletter, NewsletterCampaign
from users.email_utils import send_fleeto_email
import logging

logger = logging.getLogger(__name__)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at',)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for Newsletter model."""
    
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show count of active subscribers in changelist
        return qs
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['active_subscribers'] = Newsletter.objects.filter(is_active=True).count()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    """Admin configuration for Newsletter Campaign model."""
    
    list_display = ('subject', 'status_badge', 'recipient_count', 'created_by', 'created_at', 'sent_at', 'send_button')
    list_filter = ('status', 'created_at', 'sent_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('created_by', 'created_at', 'sent_at', 'recipient_count', 'status')
    
    fieldsets = (
        ('Newsletter Content', {
            'fields': ('subject', 'content'),
            'description': 'Write your newsletter content below. You can use simple HTML like &lt;h1&gt;, &lt;p&gt;, &lt;strong&gt;, &lt;a&gt;, etc.'
        }),
        ('Status & Tracking', {
            'fields': ('status', 'recipient_count', 'created_by', 'created_at', 'sent_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color badge."""
        if obj.status == 'sent':
            color = 'green'
            icon = '✓'
        else:
            color = 'orange'
            icon = '📝'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def send_button(self, obj):
        """Display send button for draft newsletters."""
        if obj.status == 'draft':
            return format_html(
                '<a class="button" href="{}">Send Newsletter</a>',
                f'/admin/notifications/newslettercampaign/{obj.pk}/send/'
            )
        return format_html('<span style="color: green;">✓ Sent</span>')
    send_button.short_description = 'Actions'
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user on creation."""
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_urls(self):
        """Add custom URL for sending newsletter."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:campaign_id>/send/',
                self.admin_site.admin_view(self.send_newsletter_view),
                name='send_newsletter',
            ),
        ]
        return custom_urls + urls
    
    def send_newsletter_view(self, request, campaign_id):
        """Handle sending newsletter to all active subscribers."""
        campaign = NewsletterCampaign.objects.get(pk=campaign_id)
        
        if campaign.status == 'sent':
            messages.warning(request, 'This newsletter has already been sent.')
            return redirect('admin:notifications_newslettercampaign_changelist')
        
        if request.method == 'POST':
            # Get all active subscribers
            subscribers = Newsletter.objects.filter(is_active=True)
            subscriber_emails = list(subscribers.values_list('email', flat=True))
            
            if not subscriber_emails:
                messages.warning(request, 'No active subscribers found.')
                return redirect('admin:notifications_newslettercampaign_changelist')
            
            # Send emails
            success_count = 0
            failed_count = 0
            
            for email in subscriber_emails:
                try:
                    # Create unsubscribe link
                    unsubscribe_url = f"{settings.SITE_URL}/api/newsletter/unsubscribe/"
                    
                    # Add unsubscribe link to content
                    html_content = f'''
                        {campaign.content}
                        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e9ecef; text-align: center;">
                            <p style="font-size: 12px; color: #999;">
                                You're receiving this because you subscribed to Fleeto newsletter.<br>
                                <a href="{unsubscribe_url}" style="color: #667eea;">Unsubscribe</a>
                            </p>
                        </div>
                    '''
                    
                    send_fleeto_email(
                        subject=campaign.subject,
                        text_content=campaign.get_plain_text(),  # Auto-generate plain text
                        html_content=html_content,
                        recipient_list=[email]
                    )
                    success_count += 1
                    logger.info(f"Newsletter sent to {email}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send newsletter to {email}: {str(e)}")
            
            # Update campaign status
            campaign.status = 'sent'
            campaign.sent_at = timezone.now()
            campaign.recipient_count = success_count
            campaign.save()
            
            if failed_count > 0:
                messages.warning(
                    request,
                    f'Newsletter sent to {success_count} subscribers. {failed_count} failed.'
                )
            else:
                messages.success(
                    request,
                    f'Newsletter successfully sent to {success_count} subscribers!'
                )
            
            return redirect('admin:notifications_newslettercampaign_changelist')
        
        # GET request - show confirmation page
        subscriber_count = Newsletter.objects.filter(is_active=True).count()
        context = {
            'campaign': campaign,
            'subscriber_count': subscriber_count,
            'opts': self.model._meta,
            'has_permission': True,
        }
        return render(request, 'admin/send_newsletter_confirm.html', context)


