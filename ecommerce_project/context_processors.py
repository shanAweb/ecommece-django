"""
Custom context processors for global template variables.
"""
from django.conf import settings


def site_settings(request):
    """
    Add site-wide settings to template context.
    """
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
    }


