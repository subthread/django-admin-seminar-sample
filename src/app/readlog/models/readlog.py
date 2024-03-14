from django.contrib import auth
from django.db import models
from django.utils import timezone

from app.common.fields.color import ColorField


class ReadLog(models.Model):
    class Meta:
        db_table = "readlog"
        verbose_name = verbose_name_plural = "読書ログ"

    class AdminMeta:
        display_order = 1
        menu_name = "読書ログ一覧"

    created_at = models.DateTimeField("登録日時", default=timezone.localtime, editable=False)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    user = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, verbose_name="ユーザー")
    book = models.ForeignKey("Bibliographic", on_delete=models.CASCADE, verbose_name="書籍")
    read_at = models.DateField("読了日", default=timezone.localdate)

    impression = models.TextField("感想", null=True, blank=True)
    text_color = ColorField("文字色", default="#000000", blank=True)
    background_color = ColorField("背景色", default="#ffffff", blank=True)

    def __str__(self):
        return f"{self.user}：{self.book}"
