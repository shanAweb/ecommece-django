# Quick Start Guide - Django E-Commerce

## TL;DR - Get Running in 5 Minutes

### Option 1: Automated Setup (Easiest) ⚡

```bash
# 1. Copy environment file
copy env_localhost.txt .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run automated setup (creates DB, runs migrations, etc.)
python setup_local.py

# 4. Start server
python manage.py runserver
```

**Done!** Visit http://localhost:8000

---

### Option 2: Manual Setup

```bash
# 1. Setup environment
copy env_localhost.txt .env
pip install -r requirements.txt

# 2. Create PostgreSQL database (REQUIRED!)
createdb -U postgres ecommerce_db

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Create directories
mkdir media static logs

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Start server
python manage.py runserver
```

---

## ⚠️ Common Mistake

### ❌ WRONG: Thinking Django creates the database
```bash
python manage.py migrate  # This will FAIL if database doesn't exist!
```
**Error**: `django.db.utils.OperationalError: database "ecommerce_db" does not exist`

### ✅ CORRECT: Create database first, then migrate
```bash
# Step 1: Create database
createdb -U postgres ecommerce_db

# Step 2: Then run migrations
python manage.py migrate
```

---

## 🔍 Key Differences

| Database Type | Auto-Creates? | Requires Manual Creation? |
|---------------|---------------|---------------------------|
| **SQLite** | ✅ Yes (creates .db file) | ❌ No |
| **PostgreSQL** | ❌ No | ✅ Yes |
| **MySQL** | ❌ No | ✅ Yes |

**Django only creates TABLES, not DATABASES!**

---

## 📋 Pre-Requirements Checklist

Before running setup:

- [ ] Python 3.10+ installed
- [ ] PostgreSQL installed and **running**
- [ ] Redis installed and **running** (optional but recommended)
- [ ] Virtual environment created and activated

### Check if services are running:

**PostgreSQL:**
```bash
# Windows
services.msc  # Look for "postgresql" service

# Mac
brew services list | grep postgres

# Linux
sudo service postgresql status
```

**Redis:**
```bash
# Windows
redis-cli ping  # Should return "PONG"

# Mac
brew services list | grep redis

# Linux
sudo service redis-server status
```

---

## 🚀 After Setup

Once server is running, access:

- **Homepage**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/
- **API ReDoc**: http://localhost:8000/api/redoc/

---

## 🔧 Troubleshooting

### Database Connection Error
```
Error: could not connect to server
```
**Solution**: Make sure PostgreSQL is running
```bash
# Windows: Start PostgreSQL service in services.msc
# Mac: brew services start postgresql
# Linux: sudo service postgresql start
```

### Database Does Not Exist
```
Error: database "ecommerce_db" does not exist
```
**Solution**: Create the database first!
```bash
python create_database.py
# OR
createdb -U postgres ecommerce_db
```

### Redis Connection Error
```
Error: Error connecting to Redis
```
**Solution**: Start Redis server
```bash
# Windows: Run redis-server.exe
# Mac: brew services start redis
# Linux: sudo service redis-server start
```

### Module Not Found
```
ModuleNotFoundError: No module named 'django'
```
**Solution**: Activate virtual environment and install dependencies
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 📚 Need More Details?

- **Full Setup Guide**: See `SETUP_GUIDE.md`
- **Deployment Guide**: See `DEPLOYMENT.md`
- **API Documentation**: http://localhost:8000/api/docs/ (after running server)
- **Main Documentation**: See `README.md`

---

## 🎯 Testing Your Setup

After starting the server, test these endpoints:

```bash
# API Health Check
curl http://localhost:8000/api/products/

# Should return JSON with products list (empty initially)
```

Or visit in browser:
- http://localhost:8000/ - Should show the homepage
- http://localhost:8000/admin/ - Should show login page

---

## 💡 Pro Tips

1. **Use the automated script** (`setup_local.py`) - it handles everything!
2. **Keep PostgreSQL and Redis running** while developing
3. **Create a superuser** to access the admin panel
4. **Check logs** if something goes wrong: `logs/django.log`
5. **Use console email backend** in development (emails print in terminal)

---

Happy coding! 🎉


