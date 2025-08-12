import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from services.models import ServiceProvider, ProviderAvailability, Booking
from datetime import timedelta

@pytest.mark.django_db
def test_booking_must_be_future_and_available(client):
    u = User.objects.create_user("alice", password="pass")
    p_owner = User.objects.create_user("bob", password="pass")
    sp = ServiceProvider.objects.create(user=p_owner, name="Bob's Solar", service_type="solar", location="Windsor")
    # Available tomorrow
    tomorrow = timezone.now().date() + timedelta(days=1)
    ProviderAvailability.objects.create(provider=sp, date=tomorrow)

    # Valid booking
    b = Booking(customer=u, provider=sp, booking_date=tomorrow)
    b.clean()  # should not raise

    # Past booking should fail
    past = timezone.now().date() - timedelta(days=1)
    b2 = Booking(customer=u, provider=sp, booking_date=past)
    with pytest.raises(Exception):
        b2.clean()

    # Unavailable future date should fail
    unavailable = timezone.now().date() + timedelta(days=3)
    b3 = Booking(customer=u, provider=sp, booking_date=unavailable)
    with pytest.raises(Exception):
        b3.clean()
