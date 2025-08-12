from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("providers/", views.ProviderListView.as_view(), name="providers"),
    path("book/", views.book_service, name="book_service"),
    path("history/", views.user_history, name="user_history"),
    path("register/", views.register, name="register"),
    path("create-provider/", views.create_provider, name="create_provider"),
    path("provider-dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
    # Availability management
    path("provider/<int:provider_id>/availability/", views.manage_availability, name="manage_availability"),
    path("provider/<int:provider_id>/availability/<int:avail_id>/delete/", views.delete_availability, name="delete_availability"),
    # Booking actions
    path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
]
