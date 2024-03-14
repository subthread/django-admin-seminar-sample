from django.urls import path

from . import views

app_name = "readlog"

urlpatterns = [
    path("bibliographic/export", views.ExportBibliographicView.as_view(), name="export-bibliographic"),
]
