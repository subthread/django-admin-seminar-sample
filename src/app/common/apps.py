import django.contrib.admin.apps
from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.common"


# admin.site にアクセスする前に django.contrib.admin の AdminConfig.default_site を書き換える
django.contrib.admin.apps.AdminConfig.default_site = f"{CommonConfig.name}.sites.AdminSite"
