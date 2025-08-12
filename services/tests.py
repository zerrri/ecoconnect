from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import ServiceProvider, ProviderAvailability, Booking
from datetime import date, timedelta

class ServiceProviderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_service_provider_creation(self):
        provider = ServiceProvider.objects.create(
            user=self.user,
            name="Test Solar Co",
            service_type="solar",
            location="Test City"
        )
        self.assertEqual(provider.name, "Test Solar Co")
        self.assertEqual(provider.service_type, "solar")
        self.assertEqual(str(provider), "Test Solar Co - solar")

class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='customer', password='testpass123')
        self.provider_user = User.objects.create_user(username='provider', password='testpass123')
        self.provider = ServiceProvider.objects.create(
            user=self.provider_user,
            name="Test Provider",
            service_type="solar",
            location="Test City"
        )
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.availability = ProviderAvailability.objects.create(
            provider=self.provider,
            date=self.tomorrow
        )
        
    def test_valid_booking(self):
        booking = Booking.objects.create(
            customer=self.user,
            provider=self.provider,
            booking_date=self.tomorrow
        )
        self.assertEqual(booking.customer, self.user)
        self.assertEqual(booking.provider, self.provider)
        
    def test_booking_clean_validation(self):
        # Test past date validation
        past_date = timezone.now().date() - timedelta(days=1)
        booking = Booking(
            customer=self.user,
            provider=self.provider,
            booking_date=past_date
        )
        with self.assertRaises(Exception):
            booking.clean()
            
        # Test unavailable date validation
        unavailable_date = timezone.now().date() + timedelta(days=5)
        booking = Booking(
            customer=self.user,
            provider=self.provider,
            booking_date=unavailable_date
        )
        with self.assertRaises(Exception):
            booking.clean()

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.provider_user = User.objects.create_user(username='provider', password='testpass123')
        self.provider = ServiceProvider.objects.create(
            user=self.provider_user,
            name="Test Provider",
            service_type="solar",
            location="Test City"
        )
        
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to EcoConnect")
        
    def test_provider_list_page(self):
        response = self.client.get(reverse('providers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find Green Service Providers")
        
    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create an Account")
        
    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
    def test_login_required_views(self):
        # Test that login required views redirect to login
        response = self.client.get(reverse('user_history'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Login and test again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('user_history'))
        self.assertEqual(response.status_code, 200)

class FormsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.provider_user = User.objects.create_user(username='provider', password='testpass123')
        self.provider = ServiceProvider.objects.create(
            user=self.provider_user,
            name="Test Provider",
            service_type="solar",
            location="Test City"
        )
        
    def test_booking_form_validation(self):
        from .forms import BookingForm
        
        # Test valid booking
        tomorrow = timezone.now().date() + timedelta(days=1)
        form_data = {
            'provider': self.provider.id,
            'booking_date': tomorrow.strftime('%Y-%m-%d')
        }
        form = BookingForm(data=form_data)
        self.assertFalse(form.is_valid())  # Should fail because no availability
        
        # Add availability and test again
        ProviderAvailability.objects.create(
            provider=self.provider,
            date=tomorrow
        )
        form = BookingForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_provider_registration_form(self):
        from .forms import ProviderRegistrationForm
        
        form_data = {
            'name': 'New Provider',
            'service_type': 'solar',
            'location': 'New City',
            'bio': 'Test bio'
        }
        form = ProviderRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test validation
        form_data['name'] = 'A'  # Too short
        form = ProviderRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
