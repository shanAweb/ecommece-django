"""
Utility functions for users app.
"""


def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return ip


def get_device_info(request):
    """Extract device information from request."""
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    device_info = {
        'user_agent': user_agent,
        'browser': '',
        'operating_system': '',
        'device_name': '',
    }
    
    # Try to parse user agent
    if hasattr(request, 'user_agent'):
        ua = request.user_agent
        device_info['browser'] = f"{ua.browser.family} {ua.browser.version_string}".strip()
        device_info['operating_system'] = f"{ua.os.family} {ua.os.version_string}".strip()
        
        if ua.is_mobile:
            device_info['device_name'] = f"Mobile - {ua.device.family}"
        elif ua.is_tablet:
            device_info['device_name'] = f"Tablet - {ua.device.family}"
        elif ua.is_pc:
            device_info['device_name'] = f"Desktop - {ua.os.family}"
        else:
            device_info['device_name'] = "Unknown Device"
    else:
        # Fallback if django-user-agents is not available
        if 'Mobile' in user_agent:
            device_info['device_name'] = 'Mobile Device'
        elif 'Tablet' in user_agent:
            device_info['device_name'] = 'Tablet'
        else:
            device_info['device_name'] = 'Desktop'
    
    return device_info


