import traceback

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from google.auth.transport import requests
from google.oauth2 import id_token

from ..models import ServiceUser


class GoogleAuthView(View):
    def post(self, request):
        next_url = request.POST.get("next") or reverse("admin:index")

        # https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
        # 1.CSRFトークンを検証
        if not self.verify_csrf():
            return HttpResponseBadRequest()

        # 2.IDトークン確認
        id_info = self.get_id_token()
        if not id_info:
            return redirect_to_login(next_url, reverse("admin:login"))
        # print(id_info)

        # 3.アカウントを紐付ける
        user = self.user_login(id_info)

        # ログイン
        auth.login(self.request, user)

        # ログイン後ページへリダイレクト
        return HttpResponseRedirect(next_url)

    def verify_csrf(self) -> bool:
        csrf_token_cookie = self.request.COOKIES.get("g_csrf_token")
        csrf_token_body = self.request.POST.get("g_csrf_token")
        return bool(csrf_token_cookie and csrf_token_body and csrf_token_cookie == csrf_token_body)

    def get_id_token(self):
        token = self.request.POST.get("credential")
        try:
            return id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID)
        except ValueError:
            # Invalid token
            traceback.print_exc()

    def user_login(self, id_info):
        # user_model = auth.get_user_model()

        # https://developers.google.com/identity/gsi/web/reference/js-reference#credential
        google_id = id_info["sub"]
        google_icon_url = id_info.get("picture")
        mail = id_info.get("email")

        if user := ServiceUser.objects.filter(google_id=google_id).first():
            # Google ID が一致するユーザー
            pass
        elif user := ServiceUser.objects.filter(email=mail).first():
            # メールアドレスが一致するユーザー ⇒ Google ID を紐づける
            if user.google_id:
                raise PermissionDenied  # 異なる Google ID に紐づいている
            user.google_id = google_id  # このあと google_icon_url 更新時か update_last_login() で save してもらえるはず
            user.add_group(settings.GOOGLE_USER_GROUP_NAME)  # Googleログインユーザー
        else:
            # ユーザーがいない ⇒ 作る
            user = ServiceUser.objects.create(
                google_id=google_id,
                username=mail,
                email=mail,
                first_name=id_info.get("given_name", ""),
                last_name=id_info.get("family_name", ""),
                is_staff=True,
                is_active=True,
            )
            # 全ユーザー、Googleログインユーザーのグループを付ける（
            user.add_group(settings.ALL_USER_GROUP_NAME, settings.GOOGLE_USER_GROUP_NAME)

        # Googleアカウント情報で更新
        if user.google_icon_url != google_icon_url:
            user.google_icon_url = google_icon_url
            # user.last_login = timezone.localtime()    user_logged_in シグナルで update_last_login() が呼ばれるはず
            user.save()

        return user
