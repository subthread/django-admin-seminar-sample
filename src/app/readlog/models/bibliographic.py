from django.core.files.storage import storages
from django.db import models
from django.utils import timezone

from app.common.fields import ImageFileField
from app.common.utils import upload_to


class Publisher(models.Model):
    class Meta:
        db_table = "publisher"
        verbose_name = verbose_name_plural = "出版社"
        ordering = ("name",)

    class AdminMeta:
        display_order = 4
        menu_name = "出版社管理"

    created_at = models.DateTimeField("登録日時", default=timezone.localtime, editable=False)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    name = models.CharField("名前")

    def __str__(self):
        return self.name


class Author(models.Model):
    class Meta:
        db_table = "author"
        verbose_name = verbose_name_plural = "著者"
        ordering = ("name",)

    class AdminMeta:
        display_order = 3
        menu_name = "著者管理"

    created_at = models.DateTimeField("登録日時", default=timezone.localtime, editable=False)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    name = models.CharField("名前")

    def __str__(self):
        return self.name


class Bibliographic(models.Model):
    class Meta:
        db_table = "bibliographic"
        verbose_name = verbose_name_plural = "書誌情報"
        ordering = ("title", "publisher__name")

    class AdminMeta:
        display_order = 2
        menu_name = "書誌管理"

    created_at = models.DateTimeField("登録日時", default=timezone.localtime, editable=False)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    # タイトル・著者名・出版者・発行年月など、その資料を他の資料から識別す
    title = models.CharField("タイトル")
    authors = models.ManyToManyField(Author, blank=True, verbose_name="著者")
    publisher = models.ForeignKey(Publisher, on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name="出版社")
    published_at = models.DateField("発行日", null=True, blank=True)

    picture = ImageFileField(  # type:models.FileField
        "書影",
        storage=storages["resource"],
        upload_to=upload_to,
        null=True,
        blank=True,
    )
    sample = models.FileField(
        "サンプル",
        storage=storages["resource"],
        upload_to=upload_to,
        null=True,
        blank=True,
        help_text="立ち読みサンプルPDFなどがあれば登録してください",
    )
    # genre = models.ForeignKey("", on_delete=models.DO_NOTHING, null=True, verbose_name="ジャンル")

    def __str__(self):
        author = getattr(self, "author", None)
        return f"{self.title} [{author}]" if author else self.title
