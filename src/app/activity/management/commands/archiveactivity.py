import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import cached_property
from tempfile import TemporaryFile

from django.core.files import File
from django.core.management import BaseCommand, CommandParser
from django.utils import timezone

from ...executors.archiver import ActivityArchiver
from ...models import ActivityArchive, ArchivePeriod


class Command(BaseCommand):
    help = "活動履歴をアーカイブ"

    @dataclass
    class Options:
        _filename: str
        period: ArchivePeriod
        start_date: date
        end_date: date
        dry_run: bool

        @classmethod
        def create(cls, options):
            start_date = end_date = options["date"] or timezone.localdate()  # type:date
            period = options["period"]
            if period == ArchivePeriod.WEEKLY:
                start_date -= timedelta(days=start_date.weekday())
                end_date = start_date + timedelta(days=6)
            elif period == ArchivePeriod.MONTHLY:
                start_date = start_date.replace(day=1)
                # 1日から40日後（確実に翌月）の1日の1日前 = 末日まで
                end_date = (start_date + timedelta(days=40)).replace(day=1) - timedelta(days=1)
            elif period == ArchivePeriod.ANNUAL:
                start_date = start_date.replace(month=1, day=1)
                end_date = start_date.replace(year=start_date.year + 1) - timedelta(days=1)
            return cls(
                _filename=options["filename"],
                period=period,
                start_date=start_date,
                end_date=end_date,
                dry_run=options["dry_run"],
            )

        @cached_property
        def plain(self):
            return self.filename.lower().endswith(".csv")

        @cached_property
        def filename(self):
            return self._filename or self.default_name

        @cached_property
        def default_name(self):
            ext = "csv" if self.period == ArchivePeriod.WEEKLY else "zip"
            return f"{self.period}_activity_{self.start_date.strftime('%Y%m%d')}.{ext}"

        def change_ext(self, ext, filename=None):
            if not filename:
                filename = self.filename
            basename, *_ = filename.rsplit(".", maxsplit=1)
            return f"{basename}.{ext}"

    options: Options

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--filename")
        parser.add_argument("--date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())
        parser.add_argument("--period", choices=ArchivePeriod.values, default=ArchivePeriod.MONTHLY)
        parser.add_argument("--dry_run", action="store_true")

    def handle(self, *args, **options):
        self.options = self.Options.create(options)

        archiver = ActivityArchiver(self.options.start_date, self.options.end_date)
        self.make_archive(archiver)

    def make_archive(self, archiver):
        start_at = timezone.localtime()

        # 月次ログなどデータが多いとオンメモリでは処理できないかもしれないので BytesIO でなく TemporaryFile を用いる
        with TemporaryFile() as fp:
            if self.options.plain:
                # CSVファイル化
                for chunk in archiver:
                    fp.write(chunk)
            else:
                # ZIPアーカイブとしてCSVを保存
                archive = zipfile.ZipFile(fp, "w")
                zip_info = zipfile.ZipInfo(self.options.change_ext("csv"), timezone.localtime().timetuple())
                zip_info.compress_type = zipfile.ZIP_DEFLATED
                # ZipFile.write() を自前で行う
                with archive.open(zip_info, "w") as dest:
                    for chunk in archiver:
                        dest.write(chunk)
                archive.close()

            filesize = fp.tell()
            fp.seek(0)
            self.save_archive(
                fp,
                self.options.filename,
                filesize,
                note=f"{start_at.strftime('%Y-%m-%d %H:%M:%S')} 集計開始\n"
                f"{timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')} 集計完了\n",
            )

    def save_archive(self, fp, filename: str = None, filesize: int = None, note=""):
        params = dict(
            archive_period=self.options.period,
            start_period=self.options.start_date,
            end_period=self.options.end_date,
            archive=File(fp, name=filename or fp.name),
            filesize=filesize,
            note=note,
        )
        if self.options.dry_run:
            print("\n".join(f"{name}={value}" for name, value in params.items()))
            return ActivityArchive(**params)  # 保存しない
        else:
            return ActivityArchive.objects.create(**params)
