import csv
import sys
import threading
import traceback
import zipfile
from datetime import datetime
from io import StringIO
from time import sleep
from typing import Optional

from django.core.files import File
from django.db import transaction
from django.utils import timezone

from ..models import Author, Bibliographic, ImportBibliographic, ImportStatus, Publisher


class BibliographicImporter:
    def __init__(self, record: ImportBibliographic):
        self.record = record
        self.zipfile: Optional[zipfile.ZipFile] = None
        self._notices = []
        self._errors = []

    def add_notice(self, *messages):
        self._notices.extend(messages)

    def add_error(self, *messages):
        self._errors.extend(messages)

    def execute(self, preview=True):
        if preview:
            self._execute(preview)
        else:
            # transaction に入る前に処理中状態にする
            self.record.status = ImportStatus.IN_PROGRESS
            self.record.save()
            threading.Thread(target=lambda: self._execute(preview), daemon=False).start()

        return self.record

    def _execute(self, preview=True):
        with transaction.atomic():
            status = self.record.status

            try:
                # 事前チェック
                dict_reader = self.load_csv()
                if not self.check(dict_reader):
                    status = ImportStatus.ERROR
                else:
                    # インポート試行
                    self.record.count = self.import_csv(dict_reader, preview)
                    # 結果チェック
                    if self.record.count:
                        status = ImportStatus.PREVIEW if preview else ImportStatus.COMPLETE
                    else:
                        status = ImportStatus.ERROR
                        self.add_error("登録・更新されるデータがありません")

            except (IOError, Exception):
                # エラーを記録する
                status = ImportStatus.ERROR
                [self.add_error(line) for line in traceback.format_exc().splitlines()]
                print(self._notices, file=sys.stdout)
                print(self._errors, file=sys.stderr)

            finally:
                # ImportBibliographic を更新保存する
                if not preview:
                    self.record.import_at = timezone.localtime()
                self.finalize(self.record, status)
                return self.record

    def load_csv(self) -> csv.DictReader:
        dict_reader = None
        filename = self.record.file.name  # type:str
        if filename.lower().endswith(".csv"):
            # CSVファイルアップロード時
            dict_reader = self.open_csv(self.record.file.read())

        elif filename.lower().endswith(".zip"):
            # ZIPファイルから .csv を見つけて読み込む
            self.zipfile = self.open_zipfile()
            for name in self.zipfile.namelist():
                if name.lower().endswith(".csv"):
                    self.add_notice(f"{name} をインポートします")
                    dict_reader = self.open_csv(self.zipfile.open(name).read())
                    break
            else:
                raise Exception("アーカイブに .csv ファイルが含まれていません")

        else:
            raise IOError("このファイル拡張子は処理できません")

        return dict_reader

    def open_csv(self, body: bytes):
        for encoding in ("cp932", "utf-8-sig", "utf-8"):
            try:
                return csv.DictReader(StringIO(body.decode(encoding)))
            except UnicodeDecodeError:
                continue
        else:
            return csv.DictReader(StringIO(body.decode()))

    def open_zipfile(self):
        try:
            return zipfile.ZipFile(self.record.file, metadata_encoding="cp932")
        except UnicodeDecodeError:
            try:
                return zipfile.ZipFile(self.record.file, metadata_encoding="utf-8")
            except UnicodeDecodeError:
                return zipfile.ZipFile(self.record.file)

    def check(self, dict_reader: csv.DictReader) -> bool:
        # 必須列チェック
        need_fields = {"title", "publisher", "authors"}  # "published_at", "cover", "sample"
        if short_fields := need_fields.difference(set(dict_reader.fieldnames)):
            self.add_error(f"{','.join(short_fields)} 列が見つかりません")

        return not self._errors

    def import_csv(self, dict_reader: csv.DictReader, preview: bool):
        records = list(dict_reader)
        # タイトル一覧
        books = {
            book.title: book
            for book in Bibliographic.objects.filter(title__in=[record["title"] for record in records])
        }
        # 出版社一覧
        publisher_names = [record["publisher"] for record in records]
        publishers = {publisher.name: publisher for publisher in Publisher.objects.filter(name__in=publisher_names)}
        # 著者一覧
        author_names = sum([record["authors"].split("\n") for record in records], [])  # flatten
        authors = {author.name: author for author in Author.objects.filter(name__in=author_names)}

        # FIXME:サンプルなので非効率なロジックのまま（bulk_update()などを用いるべき）

        save_count = 0
        for line, record in enumerate(records, start=2):
            errors = []
            notices = []

            try:
                title = record["title"]
                publisher_name = record["publisher"]
                published_at = record.get("published_at")
                picture = record.get("cover")
                sample = record.get("sample")

                if book := books.get(title):
                    # いまある書誌情報を更新する
                    pass
                else:
                    # レコードを追加する
                    notices.append(f"新しい書誌情報を登録します『{title}』")
                    book = Bibliographic(title=title)
                    if not preview:
                        book.save()  # ManyToManyを編集する前に保存が必要

                # 出版社
                if publisher := publishers.get(publisher_name):
                    book.publisher = publisher
                else:
                    notices.append(f"新しい出版社を登録します：{publisher_name}")
                    book.publisher = publishers[publisher_name] = Publisher(name=publisher_name)
                    if not preview:
                        book.publisher.save()

                # 著者
                author_list = []
                for author_name in record["authors"].split("\n"):
                    if author := authors.get(author_name):
                        author_list.append(author)
                    else:
                        notices.append(f"新しい著者を登録します：{author_name}")
                        author = authors[author_name] = Author(name=author_name)
                        author_list.append(author)
                        if not preview:
                            author.save()
                if not preview:
                    book.authors.clear()
                    book.authors.add(*author_list)

                # 出版日
                try:
                    book.published_at = datetime.strptime(published_at, "%Y-%m-%d") if published_at else None
                except ValueError:
                    errors.append(f"出版日が不正です：{published_at}")

                # 書影
                if picture:
                    if not self.zipfile:
                        errors.append("cover を登録する場合は zip ファイルをアップロードしてください")
                    elif picture not in self.zipfile.namelist():
                        errors.append(f"cover ファイルが含まれていません：{picture}")
                    else:
                        book.picture = File(self.zipfile.open(picture), name=picture.split("/")[-1])
                else:
                    book.picture = None

                # サンプル
                if sample:
                    if not self.zipfile:
                        errors.append("sample を登録する場合は zip ファイルをアップロードしてください")
                    elif sample not in self.zipfile.namelist():
                        errors.append(f"sample ファイルが含まれていません：{sample}")
                    else:
                        book.sample = File(self.zipfile.open(sample), name=sample.split("/")[-1])
                else:
                    book.sample = None

                if not preview:
                    # 保存する
                    book.save()
                    sleep(0.5)  # FIXME:時間がかかるテイ（ここでS3へのファイルコピーも発生する）

                if not errors:
                    save_count += 1

            except (ValueError, Exception) as e:
                traceback.print_exc()
                errors.append(str(e))

            finally:
                self.add_error(*[f"{line}行目：{error}" for error in errors])
                self.add_notice(*[f"{line}行目：{notice}" for notice in notices])

        return save_count

    def finalize(self, record: ImportBibliographic, status: ImportStatus = None):
        if status:
            record.status = status
        record.result = "\n".join(self._notices)
        record.error = "\n".join(self._errors)
        record.save()
