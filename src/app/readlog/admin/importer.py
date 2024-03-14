from django.contrib import admin
from django.utils.html import format_html

from ..executor import BibliographicImporter
from ..models import ImportBibliographic, ImportStatus


class ImportStatusFilter(admin.ListFilter):
    title = "ステータス"
    parameter_name = "status"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value[-1]

    def has_output(self):
        return True

    def expected_parameters(self):
        return [self.parameter_name]

    def queryset(self, request, queryset):
        selected = self.used_parameters.get(self.parameter_name)
        if not selected:
            return queryset.filter(status__in=(ImportStatus.PREVIEW, ImportStatus.IN_PROGRESS, ImportStatus.COMPLETE))
        elif selected == "all":
            return queryset.all()
        else:
            return queryset.filter(status=selected)

    def choices(self, changelist):
        def choice_item(value, title=None):
            return {
                "selected": (selected == value) if value else (selected is None),
                "query_string": (
                    changelist.get_query_string({self.parameter_name: value})
                    if value
                    else changelist.get_query_string(remove=[self.parameter_name])
                ),
                "display": title or getattr(value, "label", value),
            }

        selected = self.used_parameters.get(self.parameter_name)
        return [
            choice_item(None, "処理中・処理済み"),
            choice_item("all", "全て"),
            choice_item(ImportStatus.COMPLETE),
            choice_item(ImportStatus.ERROR),
            choice_item(ImportStatus.CANCEL),
        ]


@admin.register(ImportBibliographic)
class ImportBibliographicAdmin(admin.ModelAdmin):
    list_display = list_display_links = ("created_at", "filename", "status", "import_at", "count")
    list_filter = (ImportStatusFilter,)
    search_fields = ("file", "note")
    date_hierarchy = "updated_at"
    fieldsets = (
        (None, {"fields": ("file", "note", "updated_at")}),
        ("更新状況", {"fields": ("status", "created_at", "import_at")}),
        ("結果", {"fields": ("count", "view_result", "view_error")}),
    )
    readonly_fields = ("created_at", "updated_at", "import_at", "status", "count", "view_result", "view_error")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        # 一度登録したら file も変更できなくする（note のみ更新できる）
        return (*readonly_fields, "file") if obj else readonly_fields

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not change:
            kwargs.update(
                {
                    "help_texts": {
                        "note": "エクスポートした .csv ファイルか、画像を含めた ZIP アーカイブをアップロードしてください。",
                    }
                }
            )
        return super().get_form(request, obj, change, **kwargs)

    def save_model(self, request, obj: ImportBibliographic, form, change):
        if not obj.id:
            # プレビュー
            record = BibliographicImporter(obj).execute(preview=True)
            if record.status == ImportStatus.PREVIEW and record.id:
                # このレコード以外のプレビューはキャンセルする
                target = ImportBibliographic.objects.filter(status=ImportStatus.PREVIEW).exclude(id=record.id)
                target.update(status=ImportStatus.CANCEL)
        elif request.POST.get("_continue") == "インポート実行":
            # インポート実行
            BibliographicImporter(obj).execute(preview=False)
        elif "_cancel" in request.POST:
            obj.status = ImportStatus.CANCEL
            super().save_model(request, obj, form, change)
        else:
            # 備考保存
            super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        return bool(obj)  # obj=None のときは False を返して「👁表示」にしたい

    @admin.display(description=ImportBibliographic._meta.get_field("result").verbose_name)
    def view_result(self, obj: ImportBibliographic):
        return self.view_text(obj.result)

    @admin.display(description=ImportBibliographic._meta.get_field("error").verbose_name)
    def view_error(self, obj: ImportBibliographic):
        return self.view_text(obj.error)

    @staticmethod
    def view_text(text: str, cols=80, rows=10, classname="vLargeTextField"):
        return (
            format_html(
                '<textarea cols="{cols}" rows="{rows}" class="{classname}" readonly>{text}</textarea>',
                cols=cols,
                rows=rows,
                classname=classname,
                text=text,
            )
            if text
            else "-"
        )
