# Quick Fix: Update Copyright to "Fleeto"

## The Issue
Emails are showing "© E-Commerce Store. All rights reserved." instead of "© Fleeto. All rights reserved."

## The Solution

### Step 1: Update .env File
Add or update this line in your `.env` file:

```env
SITE_NAME=Fleeto
```

**Location:** `d:\personal-site\.env`

### Step 2: Restart Django Server
1. Go to the terminal where Django is running
2. Press `Ctrl+C` to stop the server
3. Run the server again:
   ```bash
   python manage.py runserver
   ```

### Step 3: Test with a NEW Email
Send a new test email (old emails won't change):
- Register a new user account, OR
- Request a password reset, OR
- Place a test order

Check the NEW email - it should now say "© Fleeto. All rights reserved."

---

## Why This Happens

The email template uses `{settings.SITE_NAME}` which reads from the `.env` file.

**In settings.py:**
```python
SITE_NAME = config('SITE_NAME', default='Fleeto')
```

This means:
- If `SITE_NAME` is in `.env` → uses that value
- If `SITE_NAME` is NOT in `.env` → uses default 'Fleeto'

If your `.env` had `SITE_NAME=E-Commerce Store` or similar, that's what was showing up.

---

## Verification

After following the steps above, new emails should show:
- ✅ "© Fleeto. All rights reserved."

**Note:** Old emails you already received will NOT change. Only NEW emails will have the updated text.
