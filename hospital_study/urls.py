from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/entries", permanent=False)),
    path("admin/", admin.site.urls),
    path(
        "login",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
    ),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("logout/", auth_views.LogoutView.as_view()),
    path("", include("study.urls")),
]
