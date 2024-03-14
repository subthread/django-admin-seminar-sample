from django import forms
from django.contrib import admin
from django.core.files.storage import storages
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from app.common.utils import upload_to


class ImportFileFormField(forms.FileField):
    allowed_extensions = ("zip", "csv")
    default_validators = (FileExtensionValidator(allowed_extensions=allowed_extensions),)

    def widget_attrs(self, widget):
        return {**super().widget_attrs(widget), "accept": ",".join(f".{ext}" for ext in self.allowed_extensions)}


class ImportFileField(models.FileField):
    def formfield(self, **kwargs):
        return super().formfield(form_class=ImportFileFormField)


class ImportStatus(models.TextChoices):
    PREVIEW = "preview", "プレビュー中"
    IN_PROGRESS = "in_progress", "インポート中"
    COMPLETE = "complete", "インポート完了"
    ERROR = "error", "エラー終了"
    CANCEL = "cancel", "キャンセル"


class ImportBibliographic(models.Model):
    class Meta:
        db_table = "import_bibliographic"
        verbose_name = verbose_name_plural = "インポートファイル"
        ordering = ("-created_at",)

    class AdminMeta:
        display_order = 5
        menu_name = "書誌情報インポート"

    created_at = models.DateTimeField("アップロード日時", default=timezone.localtime, editable=False)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    import_at = models.DateTimeField("インポート日時", null=True)

    file = ImportFileField("ファイル", storage=storages["import_file"], upload_to=upload_to)
    note = models.TextField("備考メモ", blank=True)
    status = models.CharField("ステータス", choices=ImportStatus.choices, default="-")
    count = models.IntegerField("登録・更新数", null=True)
    result = models.TextField("結果", null=True)
    error = models.TextField("エラー", null=True)

    def __str__(self):
        timestamp = timezone.localtime(self.created_at).strftime("%Y-%m-%d %H:%M")
        return f"[{timestamp}] {self.filename}"

    @property
    @admin.display(description="ファイル名")
    def filename(self):
        return self.file.name.rsplit("/", 1)[-1]
