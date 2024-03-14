from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("auth", views.GoogleAuthView.as_view(), name="auth"),
]
