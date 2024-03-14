from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user"
    verbose_name = "ユーザー管理"

    # AdminSite.get_app_list() で app を並べ替える
    display_order = 99  # 最後のほうでいい
