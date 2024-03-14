from django.core.files.storage import storages
from django.db import models
from django.utils import timezone

from app.common.utils import upload_to


class ArchiveType(models.TextChoices):
    ACTIVITY = "activity", "活動履歴"


class ArchivePeriod(models.TextChoices):
    # DAILY = "daily", "日次"
    WEEKLY = "weekly", "週次"
    MONTHLY = "monthly", "月次"
    ANNUAL = "annual", "年次"


class ActivityArchive(models.Model):
    class Meta:
        db_table = "activity_archive"
        verbose_name = verbose_name_plural = "アーカイブ"

    class AdminMeta:
        menu_name = "ダウンロード"
        display_order = 99  # 最後のほうでいい

    created_at = models.DateTimeField("作成日時", default=timezone.localtime)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    # archive_type = models.CharField("アーカイブ種別", choices=ArchiveType.choices)
    archive_period = models.CharField("アーカイブ期間", choices=ArchivePeriod.choices)
    start_period = models.DateField("対象期間：開始日")
    end_period = models.DateField("対象期間：終了日")
    archive = models.FileField("アーカイブ", storage=storages["archive"], upload_to=upload_to)
    filesize = models.IntegerField("ファイルサイズ", null=True)

    note = models.TextField("備考", blank=True, default="")

    def __str__(self):
        return "".join(
            (
                ArchivePeriod(self.archive_period).label,
                # ArchiveType(self.archive_type).label,
                self.start_period.strftime("%Y-%m-%d"),
            )
        )
