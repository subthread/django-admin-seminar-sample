from dataclasses import astuple, dataclass

from django.db import models

from app.common.archive_utils import format_csv

from ..models import ActivitySummary


class ActivityArchiver:
    def __init__(self, start_date, end_date, encoding="utf-8-sig"):  # utf-8-sig or cp932
        self.queryset: models.QuerySet = (
            ActivitySummary.objects.order_by("target_date", "user_id")
            .filter(target_date__gte=start_date, target_date__lte=end_date)
            .select_related("user")
            .prefetch_related("details")
        )
        self.encoding = encoding

    def __iter__(self):
        encoding = self.encoding
        if encoding.lower() == "utf-8-sig":
            # 最初にBOMを出す
            yield "".encode(encoding)
            encoding = "utf-8"

        # ヘッダー
        yield format_csv(CsvRecord.header(), encoding=encoding)

        # summary
        for summary in self.queryset.iterator(chunk_size=1000):
            record = CsvRecord.create(summary)
            yield format_csv(astuple(record), encoding=encoding)


@dataclass
class CsvRecord:
    date: str = None
    username: str = None
    steps: int = None
    sleep: float = None
    gymnastics: str = None
    dentifrice: str = None
    morning: str = None
    snack: str = None
    activities: str = None

    @classmethod
    def header(cls):
        return ("date", "username", "steps", "sleep", "gymnastics", "dentifrice", "morning", "snack", "activities")

    @classmethod
    def create(cls, summary: ActivitySummary):
        return cls(
            date=summary.target_date.strftime("%Y/%m/%d"),
            username=summary.user.username,
            steps=summary.steps,
            sleep=summary.sleep_time,
            gymnastics=summary.gymnastics,
            dentifrice=summary.dental,
            morning=summary.morning,
            snack=summary.snack,
            activities=",".join(detail.activity for detail in summary.details.all()),
        )
