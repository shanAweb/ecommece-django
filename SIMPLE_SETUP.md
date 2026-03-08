# Simple Setup Guide - No PostgreSQL or Redis Required!

This simplified setup uses **SQLite** (built into Python) and **local memory cache** instead of PostgreSQL and Redis.

## ✅ Prerequisites

Only need:
- ✅ Python 3.10+
- ✅ That's it! No database or cache server installation needed

## 🚀 Quick Start (5 Commands)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies (much faster now!)
pip install -r requirements.txt

# 4. Run migrations (SQLite database will be created automatically)
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

**Done!** Visit http://localhost:8000

---

## 📋 What Changed?

### Removed (Not Needed):
- ❌ PostgreSQL installation
- ❌ Redis installation
- ❌ Database creation step
- ❌ Complex setup scripts

### Using Instead:
- ✅ **SQLite** - Built into Python, zero configuration
- ✅ **Local Memory Cache** - Built into Django, zero configuration
- ✅ **Database Sessions** - Stored in SQLite automatically

### Benefits:
- ⚡ Faster installation (no external dependencies)
- 🎯 Simpler setup (5 commands instead of 12)
- 💻 Works on any system (no service installation needed)
- 🔧 Perfect for development and small sites

---

## 🗄️ About SQLite

**SQLite** is a file-based database that:
- Creates `db.sqlite3` file automatically
- No installation or configuration needed
- Perfect for development and small sites
- Handles thousands of products easily

**When to Upgrade to PostgreSQL:**
- High traffic (1000+ concurrent users)
- Need advanced database features
- Production deployment with large scale

---

## 📂 What Gets Created

After running migrations:
```
personal-site/
├── db.sqlite3          # ← Your database (created automatically)
├── venv/               # ← Virtual environment
└── ... (your code)
```

---

## 🎯 Testing Your Setup

```bash
# Run the server
python manage.py runserver

# Visit these URLs:
# - Homepage:  http://localhost:8000/
# - Admin:     http://localhost:8000/admin/
# - API Docs:  http://localhost:8000/api/docs/
```

---

## 🔧 Common Commands

```bash
# Activate virtual environment
venv\Scripts\activate

# Run server
python manage.py runserver

# Create superuser (for admin access)
python manage.py createsuperuser

# Run migrations (after model changes)
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create app data backup
python manage.py dumpdata > backup.json

# Restore data
python manage.py loaddata backup.json
```

---

## 💡 Pro Tips

1. **No need to install PostgreSQL or Redis** - SQLite and local cache work great
2. **Database is portable** - Just copy `db.sqlite3` file to backup
3. **Fresh start** - Delete `db.sqlite3` and run migrations again
4. **Admin access** - Create superuser to manage products via admin panel

---

## 🚀 Next Steps After Setup

1. **Login to Admin Panel**
   - Go to http://localhost:8000/admin/
   - Use superuser credentials you created

2. **Add Some Products**
   - Click "Products" → "Add Product"
   - Upload images, set prices, etc.

3. **Create Categories**
   - Click "Categories" → "Add Category"
   - Organize your products

4. **Test the Site**
   - Visit http://localhost:8000/
   - Browse products, add to cart, etc.

---

## ⚠️ Troubleshooting

### Error: "No module named 'django'"
**Solution:**
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Port 8000 is already in use"
**Solution:**
```bash
# Run on different port
python manage.py runserver 8080
```

### Want to start fresh?
**Solution:**
```bash
# Delete database and start over
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 Performance

This simple setup handles:
- ✅ Hundreds of products
- ✅ Thousands of orders
- ✅ Multiple concurrent users
- ✅ Perfect for small businesses

**Scalable:** Easy to upgrade to PostgreSQL + Redis later when needed.

---

## 🎉 That's It!

You now have a fully functional e-commerce platform with:
- Complete product catalog
- Shopping cart
- Checkout process
- Order management
- Admin dashboard
- API endpoints

All without installing any external services! 🚀

---

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/docs/
- **Full README**: See `README.md`
- **Advanced Setup**: See `SETUP_GUIDE.md` (for PostgreSQL/Redis)

Happy coding! 🎈

