from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from ...common.widgets import ImageInput, ImageURLInput
from ..models import ServiceUser


class ServiceUserAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            "google_icon_url": ImageURLInput(css_class="icon-preview"),
            "icon": ImageInput(css_class="icon-preview"),
        }
        fields = "__all__"


@admin.register(ServiceUser)
class ServiceUserAdmin(UserAdmin):
    form = ServiceUserAdminForm
    list_display = ("icon_preview", "username", "name", "google_id", "is_staff")
    list_display_links = ("username", "name", "google_id")
    search_fields = (*UserAdmin.search_fields, "nickname")

    fieldsets = (
        (None, {"fields": ("username",)}),
        ("Googleでログイン", {"fields": ("google_id", "google_icon")}),
        ("個人情報", {"fields": ("icon", "nickname", ("last_name", "first_name"), "email")}),
        (
            "パーミッション",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("日程", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ("google_id", "google_icon")

    formfield_overrides = {
        "google_icon_url": {"widget": ImageURLInput},
        "icon": {"widget": ImageInput(css_class="icon-preview")},
    }

    def has_change_permission(self, request, obj=None):
        return obj and obj.id == request.user.id

    @admin.display(description="Googleアイコン")
    def google_icon(self, obj: ServiceUser, size="3em"):
        return self.icon(obj.google_icon_url, size)

    @admin.display(description="アイコン")
    def icon_preview(self, obj: ServiceUser, size="1.5em"):
        return self.icon(obj.icon_url, size)

    @staticmethod
    def icon(url, size):
        style = f"height:{size}; width:{size}; object-fit:contain;"
        return format_html(f'<img src="{url}" alt="{url}" style="{style}" />') if url else "-"
