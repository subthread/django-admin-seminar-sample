import zipfile
from tempfile import TemporaryFile

from django.http import FileResponse
from django.utils import timezone
from django.views import View

from ...common.archive_utils import format_csv
from ..models import Bibliographic


class ExportBibliographicView(View):
    def get(self, request):
        queryset = Bibliographic.objects.select_related("publisher").prefetch_related("authors")
        if ids := request.GET.get("ids"):
            queryset = queryset.filter(id__in=[int(i) for i in ids.split(",")])

        fp = TemporaryFile()  # with を使うと抜けたとき閉じられてしまう…
        self.archive(fp, queryset)
        fp.seek(0)
        return FileResponse(fp, as_attachment=True, filename="bibliographic.zip")

    def archive(self, fp, queryset):
        # ZIPアーカイブとしてCSVを保存
        archive = zipfile.ZipFile(fp, "w")
        filelist = []

        # CSV出力
        zip_info = zipfile.ZipInfo("bibliographic.csv", timezone.localtime().timetuple())
        zip_info.compress_type = zipfile.ZIP_DEFLATED
        with archive.open(zip_info, "w") as dest:
            dest.write(
                format_csv(("title", "publisher", "authors", "published_at", "cover", "sample"), encoding="utf-8-sig")
            )
            for record in queryset.iterator(chunk_size=1000):  # type:Bibliographic
                dest.write(self.to_csv(record))
                if record.picture:
                    filelist.append(record.picture)
                if record.sample:
                    filelist.append(record.sample)

        # 書影、サンプル等を含める
        for fp in filelist:
            archive.writestr(fp.name, fp.read(), compress_type=zipfile.ZIP_DEFLATED)
        archive.close()

        return fp.tell()

    def to_csv(self, record: Bibliographic) -> bytes:
        return format_csv(
            (
                record.title,
                record.publisher.name,
                "\n".join(author.name for author in record.authors.all()),
                record.published_at.strftime("%Y-%m-%d") if record.published_at else None,
                record.picture.name if record.picture else None,
                record.sample.name if record.sample else None,
            )
        )
