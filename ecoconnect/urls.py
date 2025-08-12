from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("services.urls")),
    path("login/", auth_views.LoginView.as_view(template_name="services/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="services/logout.html"), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="services/password_reset.html"),
        name="password_reset",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "services.views.page_not_found"
handler500 = "services.views.server_error"
