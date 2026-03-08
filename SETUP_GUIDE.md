# Django E-Commerce - Setup Guide

## Quick Start Guide

### Step 1: System Requirements

Ensure you have the following installed:
- Python 3.10 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Git

### Step 2: Database Setup

1. **Install PostgreSQL** (if not already installed)
   - Windows: Download from https://www.postgresql.org/download/windows/
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql postgresql-contrib`

2. **Create Database**
   ```bash
   # Start PostgreSQL service
   # Windows: It should start automatically
   # Mac: brew services start postgresql
   # Linux: sudo service postgresql start

   # Connect to PostgreSQL
   psql -U postgres

   # In PostgreSQL shell, run:
   CREATE DATABASE ecommerce_db;
   CREATE USER ecommerce_user WITH PASSWORD 'securepassword123';
   GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
   \q
   ```

### Step 3: Redis Setup

1. **Install Redis**
   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Mac: `brew install redis`
   - Linux: `sudo apt-get install redis-server`

2. **Start Redis**
   ```bash
   # Windows: Run redis-server.exe
   # Mac: brew services start redis
   # Linux: sudo service redis-server start
   ```

### Step 4: Project Setup

1. **Navigate to project directory**
   ```bash
   cd personal-site
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Environment Configuration

1. **Copy the example environment file**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file with your settings**

   Required settings:
   ```env
   # Django
   DEBUG=True
   SECRET_KEY=your-secret-key-here-generate-a-new-one
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=ecommerce_db
   DB_USER=ecommerce_user
   DB_PASSWORD=securepassword123
   DB_HOST=localhost
   DB_PORT=5432

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # Stripe (Get from https://dashboard.stripe.com/test/apikeys)
   STRIPE_PUBLIC_KEY=pk_test_your_key_here
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

   # Email (for Gmail)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@ecommerce.com
   ```

   **To generate a SECRET_KEY**, run:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Step 6: Create PostgreSQL Database

**IMPORTANT**: Django does NOT automatically create the PostgreSQL database!

You must create it manually first:

```bash
# Method 1: Quick automated setup (Recommended)
python setup_local.py

# Method 2: Manual database creation
# Option A - Using createdb command
createdb -U postgres ecommerce_db

# Option B - Using psql
psql -U postgres
CREATE DATABASE ecommerce_db;
\q

# Option C - Using Python helper script
python create_database.py
```

### Step 7: Database Migrations

**Now** you can run migrations (after database exists):

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Step 8: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### Step 9: Create Required Directories

```bash
# Create directories for media files, static files, and logs
mkdir media
mkdir static
mkdir logs
```

### Step 10: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 11: Load Sample Data (Optional)

```bash
# Load sample data fixtures
python manage.py loaddata fixtures/categories.json
python manage.py loaddata fixtures/brands.json
python manage.py loaddata fixtures/products.json
```

### Step 12: Run Development Server

```bash
python manage.py runserver
```

The application will be available at:
- **Frontend**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/

## Gmail App Password Setup

If using Gmail for sending emails:

1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification (if not already enabled)
4. Go to App passwords
5. Generate a new app password for "Mail"
6. Use this password in your `.env` file as `EMAIL_HOST_PASSWORD`

## Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Navigate to Developers > API keys
3. Copy your test mode keys:
   - Publishable key (starts with `pk_test_`)
   - Secret key (starts with `sk_test_`)
4. Add them to your `.env` file

## Testing the Installation

1. **Access the homepage**: http://localhost:8000/
2. **Login to admin**: http://localhost:8000/admin/
3. **View API docs**: http://localhost:8000/api/docs/

## Common Issues and Solutions

### Issue: Database connection error
**Solution**: Ensure PostgreSQL is running and credentials in `.env` are correct.

```bash
# Check PostgreSQL status
# Windows: Check Services
# Mac: brew services list
# Linux: sudo service postgresql status
```

### Issue: Redis connection error
**Solution**: Ensure Redis is running.

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

### Issue: Module not found error
**Solution**: Ensure virtual environment is activated and dependencies are installed.

```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Static files not loading
**Solution**: Run collectstatic command.

```bash
python manage.py collectstatic --noinput
```

### Issue: Migration errors
**Solution**: Delete migration files and recreate them.

```bash
# Delete all migration files except __init__.py in each app's migrations folder
# Then run:
python manage.py makemigrations
python manage.py migrate
```

## Development Workflow

1. **Make changes** to your code
2. **Create migrations** if models changed:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
3. **Run tests**:
   ```bash
   python manage.py test
   ```
4. **Collect static files** if CSS/JS changed:
   ```bash
   python manage.py collectstatic
   ```

## Next Steps

1. **Add sample products** through the admin panel
2. **Configure email settings** for notifications
3. **Set up Stripe webhook** for payment confirmations
4. **Customize templates** in the `templates` directory
5. **Add your branding** (logo, colors, etc.)

## Production Deployment

For production deployment, please refer to:
- Django deployment checklist: https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use a production-grade web server (Gunicorn + Nginx)
- Set up SSL certificates
- Configure static files serving (WhiteNoise or CDN)
- Set up regular database backups
- Configure monitoring and logging

## Support

For issues or questions:
- Check the README.md for detailed documentation
- Review the API documentation at /api/docs/
- Check Django documentation: https://docs.djangoproject.com/

## Useful Commands

```bash
# Create a new Django app
python manage.py startapp appname

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run on different port
python manage.py runserver 8080

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Check for issues
python manage.py check

# Show migrations
python manage.py showmigrations

# Create fixture from data
python manage.py dumpdata app.Model > fixture.json

# Load fixture
python manage.py loaddata fixture.json
```

Happy coding!

