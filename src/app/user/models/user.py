from django.contrib import admin
from django.contrib.auth.models import AbstractUser, Group
from django.core.files.storage import storages
from django.db import models

from app.common.fields import ImageFileField
from app.common.utils import upload_to


class ServiceUser(AbstractUser):
    class Meta:
        db_table = "service_user"
        verbose_name = verbose_name_plural = "ユーザー情報"
        ordering = ("date_joined",)

    class AdminMeta:
        menu_name = "ユーザー一覧"

    # --- AbstractBaseUser
    # password # パスワード
    # last_login # 最終アクセス日（最終ログイン日時）
    # --- PermissionsMixin
    # is_superuser
    # groups
    # user_permissions
    # --- AbstractUser
    # username  # ログインID
    # first_name # 名
    # last_name # 姓
    # email  # メールアドレス
    # is_staff
    # is_active
    # date_joined # 作成日

    nickname = models.CharField("ニックネーム", null=True, blank=True)

    google_id = models.CharField("GoogleユーザーID", null=True, blank=True)
    google_icon_url = models.URLField("GoogleアイコンURL", null=True, blank=True)
    icon = ImageFileField(  # type:models.FileField
        "アイコン",
        storage=storages["resource"],
        upload_to=upload_to,
        null=True,
        blank=True,
        max_file_size=10 * 1024 * 1024,  # 10MB
    )

    def __str__(self):
        return self.name

    def get_full_name(self):
        return " ".join([self.last_name, self.first_name]).strip()

    @property
    @admin.display(description="名前", ordering="nickname")
    def name(self):
        return self.nickname or self.get_full_name() or self.username

    @property
    def icon_url(self):
        return getattr(self.icon, "url") if self.icon else self.google_icon_url

    def add_group(self, *names):
        self.groups.add(*Group.objects.filter(name__in=names))
