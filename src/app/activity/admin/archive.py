from datetime import date

from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils.html import format_html

from ..models import ActivityArchive


@admin.register(ActivityArchive)
class ActivityArchiveAdmin(admin.ModelAdmin):
    list_display = ("archive_period", "period", "download", "updated_at")
    list_display_links = tuple(filter(lambda name: name != "download", list_display))
    list_filter = ("archive_period",)
    ordering = ("-end_period", "archive_period")
    date_hierarchy = "end_period"
    readonly_fields = ("archive_period", "period", "download_button", "created_at", "updated_at")
    fieldsets = (
        ("アーカイブ情報", {"fields": ("archive_period", "period", "download_button")}),
        ("記録", {"fields": ("note",)}),
        ("更新情報", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return bool(obj)

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="対象期間", ordering="end_period")
    def period(self, obj: ActivityArchive):
        def format_date(dt: date):
            weekday = "月火水木金土日"[dt.weekday()]
            return f"{dt.year}年{dt.month}月{dt.day}日({weekday})"  # strftime()だと 0埋め月日になるので

        return f"{format_date(obj.start_period)}〜{format_date(obj.end_period)}"

    @admin.display(description="アーカイブ")
    def download(self, obj: ActivityArchive, suffix=""):
        if not suffix and obj.filesize:
            filesize = filesizeformat(obj.filesize)
            suffix = f"（{filesize}）"
        return format_html(
            f'<div class="object-tools" style="float: none; margin: -3px 0">'
            f'<a href="{obj.archive.url}" class="viewlink">ダウンロード{suffix}</a>'
            "</div>"
        )

    @admin.display(description="アーカイブ")
    def download_button(self, obj: ActivityArchive):
        try:
            filesize = filesizeformat(obj.filesize or obj.archive.size)
            return self.download(obj, f"（{filesize}）")
        except (FileNotFoundError, IOError, Exception):
            return format_html(f"{self.download(obj)}（NotFound）")
