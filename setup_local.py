"""
Complete Local Setup Script for Django E-Commerce Platform
This script automates the entire setup process.

Usage: python setup_local.py
"""
import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from decouple import config

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(message):
    """Print a step message."""
    print(f"\n{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'='*60}{Colors.ENDC}")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def check_env_file():
    """Check if .env file exists."""
    print_step("Step 1: Checking Environment Configuration")
    
    if not os.path.exists('.env'):
        print_error(".env file not found!")
        print("\nPlease create .env file:")
        print("  copy env_localhost.txt .env")
        return False
    
    print_success(".env file exists")
    return True

def create_database():
    """Create PostgreSQL database if it doesn't exist."""
    print_step("Step 2: Creating PostgreSQL Database")
    
    DB_NAME = config('DB_NAME', default='ecommerce_db')
    DB_USER = config('DB_USER', default='postgres')
    DB_PASSWORD = config('DB_PASSWORD', default='postgres123')
    DB_HOST = config('DB_HOST', default='localhost')
    DB_PORT = config('DB_PORT', default='5432')
    
    try:
        # Connect to PostgreSQL server
        print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            dbname='postgres',
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
            print_success(f"Database '{DB_NAME}' already exists")
        else:
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print_success(f"Database '{DB_NAME}' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print_error("Could not connect to PostgreSQL server")
        print(f"\nDetails: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Credentials in .env are correct")
        print("  3. PostgreSQL service is started")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def run_command(command, description):
    """Run a shell command and return success status."""
    try:
        print(f"\nRunning: {description}...")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print_success(description)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Create required directories."""
    print_step("Step 3: Creating Required Directories")
    
    directories = ['media', 'static', 'logs', 'staticfiles']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print_success(f"Created {directory}/ directory")
        else:
            print(f"  {directory}/ already exists")
    
    return True

def run_migrations():
    """Run Django migrations."""
    print_step("Step 4: Running Database Migrations")
    
    # Makemigrations
    if not run_command('python manage.py makemigrations', 'Creating migrations'):
        return False
    
    # Migrate
    if not run_command('python manage.py migrate', 'Applying migrations'):
        return False
    
    return True

def collect_static():
    """Collect static files."""
    print_step("Step 5: Collecting Static Files")
    
    return run_command(
        'python manage.py collectstatic --noinput',
        'Collecting static files'
    )

def create_superuser_prompt():
    """Prompt to create superuser."""
    print_step("Step 6: Create Superuser Account")
    
    response = input("\nDo you want to create a superuser now? (y/n): ").lower()
    
    if response == 'y':
        print("\nPlease enter superuser details:")
        os.system('python manage.py createsuperuser')
        return True
    else:
        print_warning("Skipped superuser creation")
        print("You can create one later with: python manage.py createsuperuser")
        return True

def main():
    """Main setup function."""
    print(f"{Colors.HEADER}")
    print("="*60)
    print("  Django E-Commerce Platform - Local Setup")
    print("="*60)
    print(f"{Colors.ENDC}")
    
    # Check environment file
    if not check_env_file():
        sys.exit(1)
    
    # Create database
    if not create_database():
        print_error("\nSetup failed: Could not create database")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print_error("\nSetup failed: Could not create directories")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print_error("\nSetup failed: Migrations failed")
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        print_warning("\nWarning: Could not collect static files (non-critical)")
    
    # Create superuser
    create_superuser_prompt()
    
    # Final success message
    print(f"\n{Colors.OKGREEN}")
    print("="*60)
    print("  🎉 Setup Complete! 🎉")
    print("="*60)
    print(f"{Colors.ENDC}")
    
    print("\n📋 Next Steps:")
    print(f"  1. Start Redis server (if not running)")
    print(f"  2. Run development server: {Colors.BOLD}python manage.py runserver{Colors.ENDC}")
    print(f"  3. Access the site:")
    print(f"     • Frontend:  http://localhost:8000/")
    print(f"     • Admin:     http://localhost:8000/admin/")
    print(f"     • API Docs:  http://localhost:8000/api/docs/")
    
    print("\n✨ Happy coding!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


