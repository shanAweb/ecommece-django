# Django E-Commerce Platform

A full-featured, production-ready e-commerce platform built with Django, Django REST Framework, and Bootstrap 5.

## Features

### 🔐 Advanced Authentication System
- JWT-based authentication with access and refresh tokens
- Multi-device session tracking with device fingerprinting
- Email verification
- Password reset via secure tokens
- "Remember Me" functionality
- "Logout from all devices" support

### 🛍️ Product Management
- Complete CRUD operations for products
- Product variants (size, color, etc.)
- Category and subcategory hierarchy (unlimited depth)
- Product image gallery
- Inventory management with low-stock alerts
- SEO-friendly URLs and meta tags
- Product attributes and specifications
- Related products

### 🛒 Shopping Experience
- Persistent shopping cart
- Save for later functionality
- Guest checkout option
- Wishlist management
- Product reviews and ratings
- Advanced search and filtering
- Product sorting options

### 💳 Payment & Checkout
- Stripe payment integration
- Multi-step checkout process
- Multiple shipping addresses
- Shipping method selection
- Coupon and discount codes
- Order tracking

### 📊 Admin Dashboard
- Sales analytics with charts
- Revenue metrics
- Inventory management
- Order management
- Customer statistics
- Top-selling products
- Marketing tools (coupons, promotions)

### 📧 Notifications
- Email notifications for orders, shipping, delivery
- Newsletter subscription
- In-app notifications

## Technology Stack

### Backend
- **Framework**: Django 5.0
- **API**: Django REST Framework 3.14
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Caching**: Redis
- **Payment**: Stripe
- **Image Processing**: Pillow

### Frontend
- **CSS Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JS (for API interactions)

## Project Structure

```
personal-site/
├── ecommerce_project/         # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── context_processors.py
├── users/                      # User management & auth
│   ├── models.py              # User, UserSession, Address, PasswordResetToken
│   ├── views.py               # Registration, login, logout, profile
│   ├── serializers.py
│   └── utils.py
├── products/                   # Product catalog
│   ├── models.py              # Product, Category, Brand, ProductVariant
│   ├── views.py               # Product listing, detail, filters
│   ├── serializers.py
│   └── admin.py
├── cart/                       # Shopping cart
│   ├── models.py              # Cart, CartItem, SavedForLater
│   ├── views.py
│   └── serializers.py
├── orders/                     # Order management
│   ├── models.py              # Order, OrderItem, Coupon, ShippingMethod
│   ├── views.py               # Checkout, order tracking
│   └── signals.py             # Email notifications
├── payments/                   # Payment processing
│   ├── models.py              # Payment, Refund
│   ├── views.py               # Stripe integration
│   └── admin.py
├── reviews/                    # Product reviews
│   ├── models.py              # Review, ReviewImage, ReviewHelpful
│   └── views.py
├── wishlist/                   # User wishlist
│   ├── models.py
│   └── views.py
├── search/                     # Search functionality
│   ├── models.py              # SearchQuery
│   └── views.py
├── notifications/              # Notifications & newsletter
│   ├── models.py              # Notification, Newsletter
│   └── views.py
├── analytics/                  # Admin analytics
│   └── views.py               # Dashboard stats, sales charts
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   └── products/
│       ├── product_list.html
│       └── product_detail.html
└── static/                     # Static files (CSS, JS, images)
```

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6+

### Setup Instructions

1. **Clone the repository**
   ```bash
   cd personal-site
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE ecommerce_db;
   CREATE USER ecommerce_user WITH PASSWORD 'your_password';
   ALTER ROLE ecommerce_user SET client_encoding TO 'utf8';
   ALTER ROLE ecommerce_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE ecommerce_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
   ```

5. **Configure environment variables**
   ```bash
   # Copy example env file
   copy .env.example .env
   
   # Edit .env and set your values:
   # - SECRET_KEY
   # - Database credentials
   # - Stripe API keys
   # - Email settings
   # - Redis URL
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Create media and static directories**
   ```bash
   mkdir media
   mkdir static
   mkdir logs
   ```

9. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

10. **Run development server**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Key API Endpoints

### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - Logout current session
- `POST /api/users/logout-all/` - Logout from all devices
- `POST /api/users/token/refresh/` - Refresh JWT token

### Products
- `GET /api/products/` - List products (with filters)
- `GET /api/products/{slug}/` - Product details
- `GET /api/products/featured/` - Featured products
- `GET /api/products/categories/` - List categories

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add/` - Add item to cart
- `PUT /api/cart/items/{id}/update/` - Update cart item
- `DELETE /api/cart/items/{id}/remove/` - Remove cart item

### Orders
- `GET /api/orders/` - List user's orders
- `POST /api/orders/create/` - Create order from cart
- `GET /api/orders/{order_number}/` - Order details
- `POST /api/orders/{order_number}/cancel/` - Cancel order

### Payments
- `POST /api/payments/{order_number}/create-intent/` - Create Stripe payment intent
- `POST /api/payments/{order_number}/confirm/` - Confirm payment

### Reviews
- `GET /api/reviews/product/{product_id}/` - Product reviews
- `POST /api/reviews/create/` - Create review
- `POST /api/reviews/{review_id}/helpful/` - Mark review as helpful

### Wishlist
- `GET /api/wishlist/` - Get user's wishlist
- `POST /api/wishlist/add/{product_id}/` - Add to wishlist
- `DELETE /api/wishlist/remove/{product_id}/` - Remove from wishlist

## Admin Panel

Access the Django admin at `http://localhost:8000/admin/`

The admin panel includes:
- User management
- Product catalog management
- Order management
- Coupon management
- Category and brand management
- Newsletter subscribers
- Reviews moderation

## Configuration

### Email Settings
Configure email settings in `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Stripe Configuration
Get your Stripe keys from https://dashboard.stripe.com/apikeys
```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Redis Configuration
```env
REDIS_URL=redis://localhost:6379/0
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in settings
- [ ] Configure allowed hosts
- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Configure email backend
- [ ] Set up static file serving (WhiteNoise or CDN)
- [ ] Configure media file storage (S3)
- [ ] Set up Redis for caching
- [ ] Configure Stripe webhook endpoint
- [ ] Set up monitoring (Sentry)

### Using Docker (Optional)
```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "ecommerce_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Testing

Run tests:
```bash
python manage.py test
```

## Security Features

- CSRF protection
- XSS prevention
- SQL injection protection
- Secure password hashing (Django's default PBKDF2)
- JWT token authentication
- Rate limiting on APIs
- Input validation and sanitization
- Secure file upload restrictions

## Performance Optimization

- Database query optimization with `select_related` and `prefetch_related`
- Redis caching for frequently accessed data
- Image optimization
- Lazy loading
- Database indexing on frequently queried fields

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the repository.

## Author

Built with Django and Bootstrap 5.

---

**Note**: Remember to configure all environment variables before running in production. Never commit `.env` files or expose sensitive credentials.


