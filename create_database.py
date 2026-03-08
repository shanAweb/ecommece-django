"""
Helper script to create PostgreSQL database if it doesn't exist.
Run this BEFORE running migrations.

Usage: python create_database.py
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from decouple import config

# Database configuration from .env
DB_NAME = config('DB_NAME', default='ecommerce_db')
DB_USER = config('DB_USER', default='postgres')
DB_PASSWORD = config('DB_PASSWORD', default='postgres123')
DB_HOST = config('DB_HOST', default='localhost')
DB_PORT = config('DB_PORT', default='5432')

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to PostgreSQL server (default postgres database)
        print(f"Connecting to PostgreSQL server at {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            dbname='postgres',  # Connect to default postgres database
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{DB_NAME}' already exists.")
        else:
            # Create database
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"✅ Database '{DB_NAME}' created successfully!")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("Next steps:")
        print("1. Run migrations: python manage.py migrate")
        print("2. Create superuser: python manage.py createsuperuser")
        print("3. Run server: python manage.py runserver")
        print("="*60)
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error: Could not connect to PostgreSQL server.")
        print(f"Details: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is installed and running")
        print("2. Credentials in .env are correct")
        print("3. PostgreSQL is accepting connections")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    create_database()


