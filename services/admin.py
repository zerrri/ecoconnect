from django.contrib import admin
from .models import ServiceProvider, Booking, ProviderAvailability

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'location', 'user']
    list_filter = ['service_type', 'location']
    search_fields = ['name', 'location']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer', 'provider', 'booking_date']
    list_filter = ['booking_date', 'provider__service_type']
    search_fields = ['customer__username', 'provider__name']

@admin.register(ProviderAvailability)
class ProviderAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['provider', 'date']
    list_filter = ['date', 'provider__service_type']
    search_fields = ['provider__name']
