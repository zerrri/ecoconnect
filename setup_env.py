#!/usr/bin/env python3
"""
Setup script for EcoConnect environment variables.
This script helps you set up the required environment variables for development.
"""

import os
import secrets
import sys

def generate_secret_key():
    """Generate a secure secret key for Django."""
    return secrets.token_urlsafe(50)

def create_env_file():
    """Create a .env file with default development settings."""
    env_content = f"""# EcoConnect Environment Variables
# Development Settings

# Django Secret Key (change this in production!)
DJANGO_SECRET_KEY={generate_secret_key()}

# Debug mode (set to False in production)
DJANGO_DEBUG=True

# Allowed hosts (comma-separated)
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# CSRF trusted origins (for HTTPS in production)
DJANGO_CSRF_TRUSTED_ORIGINS=

# Email settings (console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@ecoconnect.local

# Database (SQLite for development, PostgreSQL for production)
# DATABASE_URL=postgresql://user:password@localhost:5432/ecoconnect
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with development settings")
    print("📝 Please review and modify the settings as needed")

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def main():
    """Main setup function."""
    print("🌱 EcoConnect Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    if not os.path.exists('.env'):
        create_env_file()
    else:
        print("📁 .env file already exists")
    
    print("\n📋 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run migrations: python manage.py migrate")
    print("3. Create superuser: python manage.py createsuperuser")
    print("4. Seed demo data: python manage.py seed")
    print("5. Start server: python manage.py runserver")
    print("\n🎉 Happy coding!")

if __name__ == '__main__':
    main()
