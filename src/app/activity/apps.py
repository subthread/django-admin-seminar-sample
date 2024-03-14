from django.apps import AppConfig


class ActivityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.activity"
    verbose_name = "アクティビティ"

    # AdminSite.get_app_list() で app を並べ替える
    display_order = 1
