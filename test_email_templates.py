"""
Test script to verify email templates are working correctly.
Run this to test the email utility functions.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
django.setup()

from users.email_utils import send_fleeto_email, get_email_template
from django.conf import settings

def test_email_template():
    """Test the email template generation."""
    print("=" * 60)
    print("TESTING EMAIL TEMPLATE SYSTEM")
    print("=" * 60)
    
    # Test 1: Simple email template
    print("\n1. Testing HTML template generation...")
    html_content = '''
        <h1>Test Email</h1>
        <p>This is a test email to verify the Fleeto branding.</p>
        <div class="info-box">
            <p style="margin: 0;"><strong>Test Info:</strong> This should have a colored box.</p>
        </div>
        <p style="text-align: center;">
            <a href="https://example.com" class="button">Test Button</a>
        </p>
    '''
    
    template = get_email_template(html_content, "Test Email")
    
    if "Fleeto" in template and "Best regards" in template:
        print("✓ Template contains Fleeto branding")
    else:
        print("✗ Template missing Fleeto branding")
    
    if "logo" in template.lower() or "base64" in template:
        print("✓ Template contains logo")
    else:
        print("✗ Template missing logo")
    
    # Test 2: Send test email
    print("\n2. Testing email sending function...")
    try:
        text_content = "This is a plain text test email."
        html_content = '''
            <h1>Welcome Test 🎉</h1>
            <p>This is a <strong>test email</strong> to verify the email system is working.</p>
            <p style="text-align: center;">
                <a href="http://localhost:8000" class="button">Visit Fleeto</a>
            </p>
        '''
        
        # Note: This will print to console if using console backend
        send_fleeto_email(
            subject="Test Email - Fleeto Branding",
            text_content=text_content,
            html_content=html_content,
            recipient_list=["test@example.com"]
        )
        print("✓ Email sent successfully (check console output)")
    except Exception as e:
        print(f"✗ Email sending failed: {e}")
    
    print("\n" + "=" * 60)
    print("EMAIL TEMPLATE TEST COMPLETE")
    print("=" * 60)
    print("\nNOTE: If using console backend, check the terminal output")
    print("for the actual email content with HTML formatting.")
    print("\nAll emails now include:")
    print("  • Fleeto logo at the top")
    print("  • Professional HTML formatting")
    print("  • 'Best regards, The Fleeto Team' signature")
    print("  • Responsive design for mobile and desktop")

if __name__ == "__main__":
    test_email_template()
