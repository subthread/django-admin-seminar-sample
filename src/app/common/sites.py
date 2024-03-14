from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


class AdminSite(admin.AdminSite):
    site_title = "勉強会サンプルadmin"  # <title>タグ
    site_header = "勉強会サンプル"  # ヘッダー部分の表示
    index_title = "トップページ"  # トップページタイトル

    login_template = "admin/g_login.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.disable_action("delete_selected")    # 「選択された〇〇削除」のまとめて操作actionを消す場合ココ

    @method_decorator(never_cache)
    def login(self, request, extra_context=None):
        response = super().login(
            request,
            extra_context={
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "auth_url": request.build_absolute_uri(reverse("user:auth")),
                **(extra_context or {}),
            },
        )
        response["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        return response

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        # スーパークラスで作った app_list を加工する

        for app in app_list:
            # 各 app に AppConfig そのものを追加
            app["app_config"] = apps.get_app_config(app["app_label"])

            for app_model in app["models"]:
                # 各 model に AdminMeta を取ってきて加える
                app_model["admin"] = admin_meta = getattr(app_model["model"], "AdminMeta", None)
                # AdminMeta で menu_name が指定されていたら name を上書きする
                app_model["name"] = getattr(admin_meta, "menu_name", app_model["name"])

            # model の表示順をソート
            app["models"].sort(key=lambda app_model: getattr(app_model["admin"], "display_order", 9999))

        # app の表示順をソート
        app_list.sort(key=lambda app: getattr(app["app_config"], "display_order", 9999))
        return app_list
