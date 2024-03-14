from django.urls import path

from . import views

app_name = "activity"

urlpatterns = [
    path("download/recent", views.RecentActivityArchiveView.as_view(), name="download-recent"),
]
