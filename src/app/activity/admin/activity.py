from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from app.common.admin import UserFilter

from ..models import ActivityDetail, ActivitySummary


class SummaryUserFilter(UserFilter):
    add_facets = True

    def lookups(self, request, model_admin):
        # 自前の Facets対応のため count を annotate しておく & 1件以上記録があるユーザーのみを表示する
        return (
            super().lookups(request, model_admin).annotate(count=models.Count("activitysummary")).filter(count__gt=0)
        )


class ActivityDetailAdmin(admin.TabularInline):
    model = ActivityDetail
    extra = 0
    fields = (
        "activity",
        "minutes",
        "mets",
        # "details",
    )


@admin.register(ActivitySummary)
class ActivitySummaryAdmin(admin.ModelAdmin):
    list_display = (
        "formatted_date",
        "user_icon",
        "steps",
        "sleep_time",
        "gymnastics",
        "dental",
        "morning",
        "snack",
    )
    list_display_links = list_display
    list_filter = (SummaryUserFilter, "gymnastics", "dental", "morning", "snack")
    # list_display_links = ("target_date", "user")
    # list_editable = ("steps", "sleep_time", "gymnastics", "dental", "morning", "snack")
    search_fields = ("user__username", "user__nickname", "user__email", "note")
    date_hierarchy = "target_date"
    ordering = ("-target_date", "user__username")

    fieldsets = [
        (None, {"fields": ["user", "target_date"]}),
        ("活動", {"fields": [("steps", "gymnastics")], "description": "この日の活動について登録してください"}),
        ("生活", {"fields": [("sleep_time", "dental")], "description": "生活習慣を登録してください"}),
        ("食事", {"fields": [("morning", "snack")], "description": "食事について登録してください"}),
        ("備考", {"fields": ["note"], "classes": ["collapse"]}),
    ]
    autocomplete_fields = ["user"]
    inlines = [ActivityDetailAdmin]

    # save_as = True
    # save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    def get_readonly_fields(self, request, obj=None):
        return ["user", "target_date"] if obj else []

    def has_change_permission(self, request, obj: ActivitySummary = None):
        # obj=None のとき False を返すと index のリンクが ✏️編集 から 👁表示 になる
        return obj and obj.user_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        # obj=None のとき False を返すと actions の「選択された 活動記録 の削除」が無効になる
        return obj and obj.user_id == request.user.id

    @admin.display(description="ユーザー", ordering="user__username")
    def user_icon(self, summary: ActivitySummary, size="1.5em"):
        nickname = summary.user.name
        icon_url = summary.user.icon_url
        return (
            format_html(
                '<img src="{icon}" alt="{name}" style="{style}"/> {name}',
                **dict(icon=icon_url, name=nickname, style=f"height:{size}; width:{size}; object-fit:contain;"),
            )
            if icon_url
            else nickname
        )

    @admin.display(description="日付", ordering="target_date")
    def formatted_date(self, summary: ActivitySummary):
        dt = summary.target_date
        weekday = dt.weekday()
        date_text = f"{dt.year}年{dt.month}月{dt.day}日({'月火水木金土日'[weekday]})"
        style = {5: "color:blue", 6: "color:red"}.get(weekday, "")
        return format_html('<span style="{}">{}</span>', style, date_text)
