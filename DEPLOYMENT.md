# Deployment Guide

This guide covers deploying the Django E-Commerce platform to production.

## Pre-Deployment Checklist

### 1. Security Settings

Update `ecommerce_project/settings.py` for production:

```python
# Set DEBUG to False
DEBUG = False

# Set proper allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Generate a new SECRET_KEY
SECRET_KEY = 'your-new-production-secret-key'

# Enable HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 2. Database Configuration

Use production PostgreSQL database:

```env
DB_HOST=your-production-db-host
DB_NAME=your_production_db
DB_USER=your_production_user
DB_PASSWORD=strong_production_password
```

### 3. Static and Media Files

#### Option A: Use WhiteNoise (already configured)
- Static files will be served by WhiteNoise
- No additional configuration needed

#### Option B: Use AWS S3
Update `.env`:
```env
USE_S3=True
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1
```

### 4. Email Configuration

Use production email service:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_api_key
```

### 5. Stripe Configuration

Use live Stripe keys:

```env
STRIPE_PUBLIC_KEY=pk_live_your_live_key
STRIPE_SECRET_KEY=sk_live_your_live_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## Deployment Options

### Option 1: Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Collect static files**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### Option 2: Manual Deployment (Ubuntu Server)

#### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx redis-server -y

# Install supervisor for process management
sudo apt install supervisor -y
```

#### 2. Setup PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE ecommerce_db;
CREATE USER ecommerce_user WITH PASSWORD 'strong_password';
ALTER ROLE ecommerce_user SET client_encoding TO 'utf8';
ALTER ROLE ecommerce_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ecommerce_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
\q
```

#### 3. Setup Application

```bash
# Create app directory
sudo mkdir -p /var/www/ecommerce
cd /var/www/ecommerce

# Clone repository
sudo git clone your-repository-url .

# Create virtual environment
sudo python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
sudo nano .env
# Add your production settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Set proper permissions
sudo chown -R www-data:www-data /var/www/ecommerce
```

#### 4. Configure Gunicorn

Create Gunicorn socket: `/etc/systemd/system/gunicorn.socket`

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Create Gunicorn service: `/etc/systemd/system/gunicorn.service`

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecommerce
ExecStart=/var/www/ecommerce/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          ecommerce_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start Gunicorn:

```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
```

#### 5. Configure Nginx

Create Nginx config: `/etc/nginx/sites-available/ecommerce`

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/ecommerce/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/ecommerce/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### Option 3: Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. **Add Redis**
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```

6. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   # Set other environment variables
   ```

7. **Create Procfile**
   ```
   web: gunicorn ecommerce_project.wsgi --log-file -
   release: python manage.py migrate
   ```

8. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 4: Deploy to AWS EC2

1. **Launch EC2 instance**
   - Choose Ubuntu Server 22.04 LTS
   - Choose t2.medium or larger
   - Configure security groups (ports 22, 80, 443)

2. **Connect to instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Follow Manual Deployment steps** (Option 2)

4. **Configure RDS for PostgreSQL** (optional)
   - Create RDS PostgreSQL instance
   - Update database settings in `.env`

5. **Configure ElastiCache for Redis** (optional)
   - Create ElastiCache Redis cluster
   - Update Redis URL in `.env`

## Post-Deployment

### 1. Setup Monitoring

#### Install Sentry for error tracking

```bash
pip install sentry-sdk
```

Add to `settings.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True
)
```

### 2. Setup Database Backups

#### Automated PostgreSQL backups

Create backup script: `/var/www/scripts/backup_db.sh`

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/postgresql"
DB_NAME="ecommerce_db"

mkdir -p $BACKUP_DIR
pg_dump -U ecommerce_user $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -name "*.gz" -mtime +7 -delete
```

Add to crontab:

```bash
sudo crontab -e
# Add line:
0 2 * * * /var/www/scripts/backup_db.sh
```

### 3. Setup Log Rotation

Create `/etc/logrotate.d/ecommerce`:

```
/var/www/ecommerce/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 4. Setup Celery for Background Tasks (Optional)

Install Celery:

```bash
pip install celery
```

Create `ecommerce_project/celery.py`:

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
app = Celery('ecommerce_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 5. Configure Stripe Webhook

1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://yourdomain.com/api/payments/webhook/stripe/`
3. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Copy webhook secret to `.env`

## Maintenance

### Update Application

```bash
cd /var/www/ecommerce
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Monitor Logs

```bash
# Gunicorn logs
sudo journalctl -u gunicorn

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Application logs
tail -f /var/www/ecommerce/logs/django.log
```

### Performance Monitoring

```bash
# Check server resources
htop

# Check database performance
sudo -u postgres psql -d ecommerce_db -c "SELECT * FROM pg_stat_activity;"

# Check Redis
redis-cli info
```

## Troubleshooting

### Issue: 502 Bad Gateway
- Check if Gunicorn is running: `sudo systemctl status gunicorn`
- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### Issue: Static files not loading
- Ensure collectstatic was run
- Check Nginx configuration
- Verify file permissions

### Issue: Database connection error
- Check database credentials
- Ensure PostgreSQL is running
- Check firewall rules

### Issue: Redis connection error
- Ensure Redis is running: `sudo systemctl status redis`
- Check Redis URL in settings

## Security Best Practices

1. **Keep software updated**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. **Setup firewall**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

3. **Disable root login**
   Edit `/etc/ssh/sshd_config`:
   ```
   PermitRootLogin no
   ```

4. **Setup fail2ban**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

5. **Regular backups**
   - Database backups daily
   - Media files backups weekly
   - Configuration backups

6. **Monitor security**
   - Enable Django security middleware
   - Use HTTPS only
   - Regular security audits
   - Keep dependencies updated

## Performance Optimization

1. **Enable caching**
   - Redis for session storage
   - Cache frequently accessed data
   - Enable browser caching

2. **Database optimization**
   - Create proper indexes
   - Use database connection pooling
   - Regular VACUUM operations

3. **CDN for static files**
   - Use CloudFlare or AWS CloudFront
   - Reduce server load
   - Faster global delivery

4. **Load balancing** (for high traffic)
   - Multiple application servers
   - Use AWS ELB or similar
   - Distribute traffic efficiently

## Conclusion

Your Django E-Commerce platform is now deployed and ready for production use. Remember to:
- Monitor application performance
- Keep software updated
- Regular backups
- Security audits
- Performance optimization

For support, refer to the main README.md or documentation.


