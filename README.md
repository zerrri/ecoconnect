# EcoConnect 🌱

A sustainable service booking platform that connects users with eco-friendly service providers.

## Features

- **Service Provider Management**: Register and manage eco-friendly service providers
- **Booking System**: Book services with availability management
- **User Authentication**: Secure user registration and login
- **Service Categories**: Solar installation, home insulation, compost pickup, rainwater harvesting
- **Responsive Design**: Modern, mobile-friendly interface
- **Email Notifications**: Booking confirmations and cancellations

## Tech Stack

- **Backend**: Django 5.0.6
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, Custom CSS
- **Testing**: pytest, pytest-django
- **Deployment**: Gunicorn

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecoconnect
   ```

2. **Set up environment variables**
   ```bash
   # Create a .env file or set environment variables
   export DJANGO_SECRET_KEY="your-secret-key-here"
   export DJANGO_DEBUG="True"
   export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed demo data (optional)**
   ```bash
   python manage.py seed
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit the application**
   - Open http://127.0.0.1:8000 in your browser
   - Demo credentials: username: `demo`, password: `demo1234`

## Project Structure

```
ecoconnect/
├── ecoconnect/          # Django project settings
├── services/            # Main application
│   ├── models.py       # Database models
│   ├── views.py        # View logic
│   ├── forms.py        # Form definitions
│   ├── urls.py         # URL routing
│   ├── admin.py        # Admin interface
│   ├── tests.py        # Test cases
│   ├── templates/      # HTML templates
│   └── static/         # Static files (CSS, JS, images)
├── media/              # User uploaded files
├── logs/               # Application logs
├── requirements.txt    # Python dependencies
└── manage.py          # Django management script
```

## Models

### ServiceProvider
- User account association
- Service type (solar, insulation, compost, rainwater)
- Location and contact information
- Certification uploads
- Bio and pricing information

### ProviderAvailability
- Available dates for booking
- Linked to specific providers
- Prevents double-booking

### Booking
- Customer-provider relationship
- Booking date validation
- Email notifications

## Testing

Run the test suite:
```bash
python manage.py test
```

Or use pytest:
```bash
pytest
```

## Security Features

- CSRF protection on all forms
- File upload validation (size and type)
- Secure password validation
- Environment variable configuration
- SQL injection prevention
- XSS protection

## Deployment

### Production Settings

1. Set environment variables:
   ```bash
   export DJANGO_SECRET_KEY="your-production-secret-key"
   export DJANGO_DEBUG="False"
   export DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
   export DJANGO_CSRF_TRUSTED_ORIGINS="https://yourdomain.com"
   ```

2. Use a production database:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. Configure email backend:
   ```bash
   export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
   export DEFAULT_FROM_EMAIL="noreply@yourdomain.com"
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team.
