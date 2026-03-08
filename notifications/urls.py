"""
URL configuration for notifications app.
"""
from django.urls import path
from .views import (
    get_notifications, mark_notification_read, mark_all_read,
    subscribe_newsletter, unsubscribe_newsletter
)

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('', get_notifications, name='get-notifications'),
    path('<int:notification_id>/read/', mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', mark_all_read, name='mark-all-read'),
    
    # Newsletter
    path('newsletter/subscribe/', subscribe_newsletter, name='subscribe-newsletter'),
    path('newsletter/unsubscribe/', unsubscribe_newsletter, name='unsubscribe-newsletter'),
]


