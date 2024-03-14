from django.apps import AppConfig


class ReadLogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.readlog"
    verbose_name = "読書ログ"

    # AdminSite.get_app_list() で app を並べ替える
    display_order = 2
