from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from ...common.widgets import ImageInput
from ..models import Author, Bibliographic, Publisher


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ("name",)


class BibliographicAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            "picture": ImageInput(css_class="picture-preview"),
        }
        fields = "__all__"


@admin.action(description=f"選択された {Bibliographic._meta.verbose_name} をエクスポート")
def export_selected(model_admin, request, queryset):
    return HttpResponseRedirect(
        "{}?ids={}".format(reverse("readlog:export-bibliographic"), ",".join(str(obj.id) for obj in queryset))
    )


@admin.register(Bibliographic)
class BibliographicAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("title", "author", "publisher")
    search_fields = ("title", "authors__name", "publisher__name")
    list_filter = ("authors", "publisher")
    show_facets = admin.ShowFacets.ALWAYS
    actions = (export_selected,)

    form = BibliographicAdminForm
    fieldsets = (
        ("書誌情報", {"fields": ("title", "authors", "publisher", "published_at")}),
        ("ファイル", {"fields": ("picture", "sample")}),
    )
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("authors",)
    autocomplete_fields = ("publisher",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("publisher").prefetch_related("authors")

    @admin.display(description="著者")
    def author(self, obj: Bibliographic, max_authors=3):
        authors = [author.name for author in obj.authors.all()]
        return ",".join([*authors[:max_authors], "et al."] if max_authors and len(authors) > max_authors else authors)

    def get_fieldsets(self, request, obj=None):
        return [*self.fieldsets, ("登録情報", {"fields": ("created_at", "updated_at")})] if obj else self.fieldsets
