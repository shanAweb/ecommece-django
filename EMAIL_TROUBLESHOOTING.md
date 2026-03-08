# Email Troubleshooting Guide

## Issue: Emails Showing Raw HTML or Logo Not Loading

If you're seeing raw HTML in emails or the logo isn't displaying, here's how to fix it:

### Understanding the Email System

The Django app sends emails in **multipart/alternative** format, which includes:
1. **Plain text version** - Fallback for email clients that don't support HTML
2. **HTML version** - Professional branded email with Fleeto logo

Email clients that support HTML will automatically display the HTML version.

---

## Common Issues & Solutions

### 1. **Console Backend (Development)**

If you're using the console email backend (default for development), emails are printed to the terminal as raw text. This is NORMAL and expected.

**What you'll see in terminal:**
- Raw HTML code
- Base64 encoded logo data
- Both plain text and HTML versions

**This is NOT an error** - it's just how the console backend displays emails for debugging.

**To test actual email rendering:**
- Configure SMTP in your `.env` file (see below)
- Emails will then be sent to real email addresses where HTML will render properly

### 2. **SMTP Configuration**

To send actual emails with proper HTML rendering, configure SMTP in your `.env` file:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important for Gmail:**
- You MUST use an "App Password", not your regular Gmail password
- Go to Google Account → Security → 2-Step Verification → App passwords
- Generate a new app password for "Mail"
- Use that 16-character password in `EMAIL_HOST_PASSWORD`

**After updating `.env`:**
```bash
# Restart the Django server
# Press Ctrl+C to stop the current server
python manage.py runserver
```

### 3. **Email Client Issues**

Some email clients may have issues displaying HTML emails. Here's what we've done to maximize compatibility:

✅ **Table-based layout** - Uses HTML tables instead of divs (better email client support)  
✅ **Inline styles** - All styles are inline for maximum compatibility  
✅ **Base64 logo** - Logo is embedded directly in the email (no external image loading)  
✅ **XHTML DOCTYPE** - Uses proper email-compatible DOCTYPE  
✅ **Fallback text** - Plain text version for clients that don't support HTML  

### 4. **Testing Email Rendering**

To test if emails are rendering correctly:

1. **Configure SMTP** (see above)
2. **Trigger an email** by:
   - Registering a new user account
   - Requesting a password reset
   - Subscribing to newsletter
   - Placing an order
3. **Check your email inbox** - You should see:
   - ✅ Fleeto logo at the top
   - ✅ Purple gradient header
   - ✅ Professional HTML formatting
   - ✅ Styled buttons
   - ✅ "Best regards, The Fleeto Team" signature

### 5. **Gmail Specific Issues**

If using Gmail and emails look plain:

1. **Check the "View entire message" link** - Gmail sometimes clips emails
2. **Check if images are blocked** - Click "Display images below" if prompted
3. **Check spam folder** - Sometimes HTML emails go to spam
4. **Try another email client** - Test with Outlook, Apple Mail, etc.

---

## Verification Checklist

After configuring SMTP, verify emails are working:

- [ ] **Welcome Email** - Register new user, check for HTML email with logo
- [ ] **Email Verification** - Check verification button is styled
- [ ] **Password Reset** - Request reset, check for styled reset button
- [ ] **Contact Form** - Submit form, check customer confirmation email
- [ ] **Newsletter** - Subscribe, check for styled welcome email
- [ ] **Order Confirmation** - Place order, check for professional invoice-style email

---

## Still Having Issues?

If emails still show raw HTML after configuring SMTP:

1. **Check Django logs** - Look for email sending errors
2. **Verify SMTP credentials** - Make sure app password is correct
3. **Test with a simple email client** - Try a basic email app first
4. **Check email source** - View the raw email source to see if HTML is present
5. **Try a different email provider** - Test with Gmail, Outlook, etc.

---

## Technical Details

**Email Format:** multipart/alternative  
**HTML Version:** XHTML 1.0 Transitional with table-based layout  
**Logo Format:** Base64 encoded PNG (embedded in email)  
**Styling:** Inline CSS for maximum compatibility  
**Fallback:** Plain text version for non-HTML clients  

**Files involved:**
- `users/email_utils.py` - Email template and sending functions
- `users/signals.py` - Welcome email
- `users/views.py` - Verification, password reset, contact form emails
- `orders/signals.py` - Order notification emails
- `notifications/views.py` - Newsletter subscription email

---

## Quick Test

To quickly test if emails are working:

1. Make sure SMTP is configured in `.env`
2. Restart Django server
3. Go to your website and register a new account
4. Check your email inbox for the welcome email
5. It should display with Fleeto branding and logo

If you see the HTML email properly rendered, everything is working! 🎉
