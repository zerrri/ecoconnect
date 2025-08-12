from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import os

def validate_file_size(value):
    """Validate that uploaded files are not too large (max 5MB)"""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("File size cannot exceed 5MB.")

class ServiceProvider(models.Model):
    SERVICE_TYPES = [
        ("solar", "Solar Installation"),
        ("insulation", "Home Insulation"),
        ("compost", "Compost Pickup"),
        ("rainwater", "Rainwater Harvesting"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, db_index=True)
    location = models.CharField(max_length=100, db_index=True)
    certification = models.FileField(
        upload_to="certifications/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf", "png", "jpg", "jpeg"]),
            validate_file_size
        ],
    )
    bio = models.TextField(blank=True, default="")
    price_note = models.CharField(max_length=120, blank=True, default="")
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.service_type}"

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class ProviderAvailability(models.Model):
    """Specific dates a provider is available to take bookings."""
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="availability")
    date = models.DateField(db_index=True)

    class Meta:
        unique_together = ("provider", "date")
        ordering = ("date",)

    def __str__(self):
        return f"{self.provider.name} available on {self.date}"

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    booking_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "booking_date"], name="uniq_provider_booking_date"
            )
        ]
        ordering = ("-booking_date",)

    def clean(self):
        if self.booking_date and self.booking_date < timezone.now().date():
            raise ValidationError("Booking date must be in the future.")
        # Must be a date the provider is available
        if self.booking_date and self.provider and not ProviderAvailability.objects.filter(provider=self.provider, date=self.booking_date).exists():
            raise ValidationError("Selected date is not available for this provider.")

    def __str__(self):
        return f"{self.customer.username} booked {self.provider.name} on {self.booking_date}"
