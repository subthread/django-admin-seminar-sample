from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.db import models
from django.utils.html import format_html

from app.common.admin import UserFilter

from ..models import ReadLog


class ReadLogUserFilter(UserFilter):
    add_facets = True

    def lookups(self, request, model_admin):
        # ReadLog が 1件以上あるユーザー または 全ユーザー グループのユーザーを対象として列挙する
        return (
            super()
            .lookups(request, model_admin)
            .annotate(count=models.Count("readlog"))
            .filter(models.Q(count__gt=0) | models.Q(groups__name=settings.ALL_USER_GROUP_NAME))
            .distinct()
        )


@admin.register(ReadLog)
class ReadLogAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("user_icon", "book", "read_at")
    search_fields = ("user__username", "user__nickname", "impression")
    list_filter = (ReadLogUserFilter, "book")
    date_hierarchy = "read_at"
    ordering = ("-read_at", "book_id", "user_id")

    readonly_fields = ("user", "book", "created_at", "updated_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "book")

    def get_fieldsets(self, request, obj=None):
        color_row = (("text_color", "background_color"),) if self.has_change_permission(request, obj) else ()
        update_block = ("更新情報", {"fields": ("created_at", "updated_at")})
        return (
            (None, {"fields": ("user",)}),
            ("書誌情報", {"fields": ("book", "read_at")}),
            ("感想", {"fields": ("impression", *color_row)}),
            *((update_block,) if obj else ()),  # 追加のときは更新情報なし
        )

    def get_readonly_fields(self, request, obj=None):
        # 追加のときは readonly_fields は不要
        return super().get_readonly_fields(request, obj) if obj else ()

    def get_form(self, request, obj: ReadLog = None, change=False, **kwargs):
        widgets = kwargs.pop("widgets", {})
        if not obj:
            # 追加のときはユーザーは hidden で initial_data の request.user だけを渡す
            widgets["user"] = forms.HiddenInput()
        form_class = super().get_form(request, obj, change, **kwargs, widgets=widgets)
        if obj and not self.has_change_permission(request, obj):
            # super().get_form() で change_permission が無いときは全 fields を exclude されているので
            # 作られた form_class の base_fields を更新するしかいまのところ方法が見つからない
            form_class.base_fields["impression"] = ReadLog._meta.get_field("impression").formfield(
                widget=ColoredTextInput(obj.text_color, obj.background_color)
            )
        return form_class

    def get_changeform_initial_data(self, request):
        return {
            **super().get_changeform_initial_data(request),
            "user": request.user,
        }

    def has_change_permission(self, request, obj: ReadLog = None):
        only_view = self.has_view_permission(request, obj) and obj and obj.user_id != request.user.id
        return super().has_change_permission(request, obj) and not only_view

    @admin.display(description="ユーザー", ordering="user__username")
    def user_icon(self, summary: ReadLog, size="1.5em"):
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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        print(db_field, field)
        return field


class ColoredTextInput(AdminTextareaWidget):
    read_only = True

    def __init__(self, text_color, background_color):
        super().__init__(attrs={"style": f"color:{text_color};background-color:{background_color}", "readonly": True})
