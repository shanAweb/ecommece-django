"""
Email utility functions for sending professional branded emails.
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from email.mime.image import MIMEImage
import base64
import os


def get_logo_path():
    """Get path to Fleeto logo."""
    return os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')


def get_email_template(content, title=""):
    """
    Returns professional HTML email template with Fleeto branding.
    Uses table-based layout for maximum email client compatibility.
    
    Args:
        content: Main email content (can include HTML)
        title: Optional title/heading for the email
    
    Returns:
        HTML string for email
    """
    # Use CID (Content-ID) for logo instead of base64 for better compatibility
    # Use table-based layout for better email client support
    html = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>{title if title else 'Fleeto'}</title>
        <style type="text/css">
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background-color: #f5f5f5;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}
            table {{
                border-collapse: collapse;
            }}
            img {{
                border: 0;
                outline: none;
                text-decoration: none;
                display: block;
            }}
            .button {{
                display: inline-block;
                padding: 14px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                background-color: #667eea;
                color: #ffffff !important;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
            }}
            .info-box {{
                background-color: #f8f9ff;
                border-left: 4px solid #667eea;
                padding: 15px 20px;
                margin: 20px 0;
            }}
            @media only screen and (max-width: 600px) {{
                .content {{
                    padding: 20px !important;
                }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f5f5f5;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f5f5f5;">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <!-- Main Container -->
                    <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; max-width: 600px;">
                        <!-- Header with Logo -->
                        <tr>
                            <td align="center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-color: #667eea; padding: 40px 20px;">
                                <img src="cid:fleeto_logo" alt="Fleeto" style="max-width: 150px; height: auto;" />
                            </td>
                        </tr>
                        <!-- Content -->
                        <tr>
                            <td class="content" style="padding: 40px 30px; line-height: 1.6; color: #333333;">
                                {content}
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f9fa; padding: 30px 20px; text-align: center;">
                                <p style="margin: 0 0 10px 0; font-size: 14px; color: #6c757d;">
                                    <strong>Best regards,</strong>
                                </p>
                                <p style="margin: 0 0 20px 0; font-size: 14px; color: #6c757d;">
                                    <strong>The Fleeto Team</strong>
                                </p>
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="border-top: 1px solid #e9ecef; padding-top: 20px;">
                                            <p style="margin: 10px 0; font-size: 14px; color: #6c757d;">
                                                <a href="{settings.SITE_URL}" style="color: #667eea; text-decoration: none;">{settings.SITE_URL}</a>
                                            </p>
                                            <p style="margin: 10px 0; font-size: 12px; color: #999999;">
                                                © {settings.SITE_NAME}. All rights reserved.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html


def send_fleeto_email(subject, text_content, html_content, recipient_list, from_email=None):
    """
    Send a professional branded email with both HTML and plain text versions.
    
    Args:
        subject: Email subject
        text_content: Plain text version of email
        html_content: HTML content (will be wrapped in Fleeto template)
        recipient_list: List of recipient email addresses
        from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
    
    Returns:
        Number of emails sent
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Format sender as "Fleeto <email@example.com>"
    sender = f"Fleeto <{from_email}>"
    
    # Wrap HTML content in professional template
    html_message = get_email_template(html_content)
    
    # Create email with both HTML and text versions
    # EmailMultiAlternatives sends multipart/alternative with plain text as default
    # and HTML as alternative - email clients will prefer HTML if they support it
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # Plain text version (fallback)
        from_email=sender,  # Use formatted sender name
        to=recipient_list
    )
    
    # Attach HTML version as alternative
    # Email clients that support HTML will display this instead of plain text
    email.attach_alternative(html_message, "text/html")
    
    # Attach logo as inline image using Content-ID
    logo_path = get_logo_path()
    try:
        with open(logo_path, 'rb') as f:
            logo_data = f.read()
            logo_image = MIMEImage(logo_data)
            logo_image.add_header('Content-ID', '<fleeto_logo>')
            logo_image.add_header('Content-Disposition', 'inline', filename='logo.png')
            email.attach(logo_image)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to attach logo: {str(e)}")
    
    # Send the email
    try:
        result = email.send(fail_silently=False)
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
        raise
