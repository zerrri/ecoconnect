from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Booking, ServiceProvider, ProviderAvailability

class ProviderFilterForm(forms.Form):
    q = forms.ChoiceField(
        choices=[("", "-- Service Type --")] + list(ServiceProvider.SERVICE_TYPES),
        required=False,
        label="Service type",
    )
    location = forms.CharField(max_length=100, required=False, label="Location")

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["provider", "booking_date"]
        widgets = {
            "booking_date": forms.DateInput(attrs={"type": "date"})
        }

    def clean_booking_date(self):
        date = self.cleaned_data["booking_date"]
        if not date:
            raise ValidationError("Please select a booking date.")
        
        if date < timezone.now().date():
            raise ValidationError("Booking date must be in the future.")
        
        provider = self.cleaned_data.get("provider")
        if provider and not ProviderAvailability.objects.filter(provider=provider, date=date).exists():
            raise ValidationError("This provider is not available on that date.")
        
        return date

    def clean(self):
        cleaned_data = super().clean()
        provider = cleaned_data.get("provider")
        booking_date = cleaned_data.get("booking_date")
        
        if provider and booking_date:
            # Check if the date is already booked
            if Booking.objects.filter(provider=provider, booking_date=booking_date).exists():
                raise ValidationError("This date is already booked for the selected provider.")
        
        return cleaned_data

class ProviderRegistrationForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ["name", "service_type", "location", "certification", "bio", "price_note"]
        
    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name.strip()) < 2:
            raise ValidationError("Provider name must be at least 2 characters long.")
        return name.strip()
    
    def clean_location(self):
        location = self.cleaned_data["location"]
        if len(location.strip()) < 2:
            raise ValidationError("Location must be at least 2 characters long.")
        return location.strip()

class UploadCertificationForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = ["certification"]

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = ProviderAvailability
        fields = ["date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})
        }
    
    def clean_date(self):
        date = self.cleaned_data["date"]
        if not date:
            raise ValidationError("Please select a date.")
        
        if date < timezone.now().date():
            raise ValidationError("Availability date must be in the future.")
        
        return date
