# Email Setup Guide for Fleeto

## Current Status (Development Mode)

By default, the application is configured to use **Console Email Backend** for development/testing. This means:
- ✅ All emails are displayed in your terminal/console
- ✅ No real SMTP credentials needed
- ✅ Perfect for localhost testing
- ❌ No actual emails are sent

## When to Use Real SMTP

You need real SMTP credentials when you want to:
- Send actual emails to users
- Test email delivery in production
- Test email notifications on real email addresses

## How to Setup Real SMTP (Gmail Example)

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Scroll down to **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password

### Step 2: Update `.env` File

Open your `.env` file and update the email configuration:

```env
# Change from console to SMTP backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Gmail SMTP settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Your Gmail credentials
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# From email (must match your Gmail)
DEFAULT_FROM_EMAIL=Fleeto <your-email@gmail.com>
```

### Step 3: Restart Django Server

After updating `.env`, restart your Django development server:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

## Other Email Providers

### SendGrid

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=Fleeto <noreply@yourdomain.com>
```

### Mailgun

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@yourdomain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-smtp-password
DEFAULT_FROM_EMAIL=Fleeto <noreply@yourdomain.com>
```

### Amazon SES

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-ses-smtp-username
EMAIL_HOST_PASSWORD=your-ses-smtp-password
DEFAULT_FROM_EMAIL=Fleeto <noreply@yourdomain.com>
```

## Email Features in Fleeto

Once SMTP is configured, the following emails will be sent automatically:

### 1. User Registration Email
- **Trigger**: New user signs up
- **Content**: Email verification link
- **Log**: `[email] Sending verification email`

### 2. Password Reset Email
- **Trigger**: User requests password reset
- **Content**: Password reset link
- **Log**: `[email] Sending password reset email`

### 3. Order Status Email
- **Trigger**: Order status changes
- **Content**: Order number, new status, items
- **Log**: `[email] Sending order status change email`

### 4. Newsletter Subscription Email
- **Trigger**: User subscribes to newsletter
- **Content**: Subscription confirmation
- **Log**: `[email] Sending newsletter subscription confirmation`

### 5. Contact Form Emails
- **Trigger**: User submits contact form
- **Content**: 
  - To Admin: Full contact form details
  - To Customer: Confirmation that message was received
- **Log**: `[CONTACT FORM] New submission`

## Testing Emails

### With Console Backend (Current Setup)
```bash
# Start the server
python manage.py runserver

# Submit the contact form or perform any action that sends email
# Check your terminal - the email content will be printed there
```

### With SMTP Backend (Real Emails)
```bash
# Update .env with real SMTP credentials
# Restart server
python manage.py runserver

# Submit the contact form or perform any action that sends email
# Check the recipient's email inbox
```

## Troubleshooting

### Gmail "Less Secure App" Error
- Use an **App Password** instead of your regular password
- Make sure 2-Step Verification is enabled

### Emails Not Sending
1. Check terminal logs for error messages
2. Verify SMTP credentials are correct
3. Ensure EMAIL_BACKEND is set to `smtp.EmailBackend` (not `console.EmailBackend`)
4. Check if your email provider requires special settings

### Emails Going to Spam
- Set up SPF, DKIM, and DMARC records for your domain
- Use a verified sender email address
- Consider using a dedicated email service (SendGrid, Mailgun, etc.)

## Questions?

If you encounter any issues:
1. Check the terminal logs (all email events are logged)
2. Verify your `.env` file configuration
3. Test with Gmail first (easiest to set up)
4. Make sure you restart the server after changing `.env`

