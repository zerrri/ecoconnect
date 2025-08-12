from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import ServiceProvider, ProviderAvailability
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Seed demo users, providers, and availability"

    def handle(self, *args, **kwargs):
        u, _ = User.objects.get_or_create(username="demo", defaults={"email":"demo@example.com"})
        u.set_password("demo1234")
        u.save()
        p, _ = ServiceProvider.objects.get_or_create(
            user=u, name="Eco Solar Co", service_type="solar", location="Windsor",
            defaults={"bio": "Solar installs and maintenance.", "price_note": "From $99 inspection"}
        )
        # Next 10 days every other day
        ProviderAvailability.objects.filter(provider=p).delete()
        today = date.today()
        for i in range(1, 11, 2):
            ProviderAvailability.objects.create(provider=p, date=today + timedelta(days=i))
        self.stdout.write(self.style.SUCCESS("Seeded demo data."))
