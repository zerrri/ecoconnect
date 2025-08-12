from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, TemplateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

from .models import ServiceProvider, Booking, ProviderAvailability
from .forms import (
    BookingForm, ProviderRegistrationForm, UserRegisterForm,
    ProviderFilterForm, AvailabilityForm
)

# Set up logging
logger = logging.getLogger(__name__)

# ---------- Pages ----------

class HomeView(TemplateView):
    template_name = "services/home.html"

class ProviderListView(ListView):
    template_name = "services/provider_list.html"
    context_object_name = "providers"
    model = ServiceProvider
    paginate_by = 12

    def get_queryset(self):
        qs = ServiceProvider.objects.all().select_related("user")
        q = self.request.GET.get("q")
        loc = self.request.GET.get("location")
        if q:
            qs = qs.filter(service_type=q)
        if loc:
            qs = qs.filter(location__icontains=loc)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = ProviderFilterForm(self.request.GET or None)
        return ctx

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, "Registration successful.")
                return redirect("home")
            except Exception as e:
                logger.error(f"Registration failed: {e}")
                messages.error(request, "Registration failed. Please try again.")
    else:
        form = UserRegisterForm()
    return render(request, "services/register.html", {"form": form})

@login_required
def create_provider(request):
    if request.method == "POST":
        form = ProviderRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                provider = form.save(commit=False)
                provider.user = request.user
                provider.save()
                messages.success(request, "Your service profile has been created.")
                return redirect("provider_dashboard")
            except Exception as e:
                logger.error(f"Provider creation failed: {e}")
                messages.error(request, "Failed to create service profile. Please try again.")
    else:
        form = ProviderRegistrationForm()
    return render(request, "services/create_provider.html", {"form": form})

@login_required
def manage_availability(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id, user=request.user)
    
    if request.method == "POST":
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.provider = provider
                if obj.date < timezone.now().date():
                    messages.error(request, "Availability must be a future date.")
                else:
                    obj.save()
                    messages.success(request, f"Added availability for {obj.date}.")
            except Exception as e:
                logger.error(f"Availability creation failed: {e}")
                messages.error(request, "Failed to add availability. Please try again.")
            return redirect("manage_availability", provider_id=provider.id)
    else:
        form = AvailabilityForm()

    # Existing availability with simple pagination
    av_qs = provider.availability.order_by("date")
    page = Paginator(av_qs, 15).get_page(request.GET.get("page"))
    return render(request, "services/manage_availability.html", {"provider": provider, "form": form, "page": page})

@login_required
def delete_availability(request, provider_id, avail_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id, user=request.user)
    avail = get_object_or_404(ProviderAvailability, id=avail_id, provider=provider)
    try:
        avail.delete()
        messages.success(request, f"Removed availability for {avail.date}.")
    except Exception as e:
        logger.error(f"Availability deletion failed: {e}")
        messages.error(request, "Failed to remove availability.")
    return redirect("manage_availability", provider_id=provider.id)

def _send_booking_emails(booking, user):
    """Send booking confirmation emails to customer and provider"""
    try:
        # Email to customer
        if user.email:
            send_mail(
                subject="EcoConnect: Booking Confirmed",
                message=f"Your booking with {booking.provider.name} on {booking.booking_date} is confirmed.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        
        # Email to provider
        if booking.provider.user.email:
            send_mail(
                subject="EcoConnect: New Booking",
                message=f"You have a new booking on {booking.booking_date} from {user.username}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.provider.user.email],
                fail_silently=True,
            )
    except Exception as e:
        logger.error(f"Failed to send booking emails: {e}")

@login_required
def book_service(request):
    # Pre-calc disabled dates for the selected provider (or none yet)
    disabled_dates = []
    selected_provider_id = request.GET.get("provider")
    if selected_provider_id:
        p = get_object_or_404(ServiceProvider, id=selected_provider_id)
        # Disable all future days that are NOT in availability (client hint only; server validates)
        future_days = [timezone.now().date()]
        # For simplicity, just pass the list of available dates and flip logic in template
        available_dates = list(
            ProviderAvailability.objects.filter(provider=p, date__gte=timezone.now().date())
            .order_by("date")
            .values_list("date", flat=True)
        )
    else:
        p = None
        available_dates = []

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    booking = form.save(commit=False)
                    booking.customer = request.user
                    booking.save()
                    
                    # Send confirmation emails
                    _send_booking_emails(booking, request.user)
                    
                messages.success(request, "Booking confirmed.")
                return redirect("user_history")
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.error(f"Booking creation failed: {e}")
                messages.error(request, "Booking failed. Please try again.")
    else:
        form = BookingForm(initial={"provider": selected_provider_id} if selected_provider_id else None)

    return render(
        request,
        "services/book_service.html",
        {
            "form": form,
            "selected_provider": p,
            "available_dates": [d.strftime("%Y-%m-%d") for d in available_dates],
        },
    )

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    booking_date = booking.booking_date
    provider_name = booking.provider.name
    
    try:
        with transaction.atomic():
            booking.delete()
            
            # Send cancellation email
            if request.user.email:
                send_mail(
                    subject="EcoConnect: Booking Cancelled",
                    message=f"Your booking with {provider_name} on {booking_date} has been cancelled.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
        messages.success(request, "Booking cancelled.")
    except Exception as e:
        logger.error(f"Booking cancellation failed: {e}")
        messages.error(request, "Failed to cancel booking.")
    
    return redirect("user_history")

@login_required
def user_history(request):
    bookings = (
        Booking.objects.select_related("provider")
        .filter(customer=request.user)
        .order_by("-booking_date")
    )
    return render(request, "services/user_history.html", {"bookings": bookings})

@login_required
def provider_dashboard(request):
    providers = ServiceProvider.objects.filter(user=request.user)
    return render(request, "services/provider_dashboard.html", {"providers": providers})

def about_page(request):
    return render(request, "services/about.html")

def contact_page(request):
    return render(request, "services/contact.html")

def page_not_found(request, exception):
    return render(request, "services/404.html", status=404)

def server_error(request):
    return render(request, "services/500.html", status=500)
