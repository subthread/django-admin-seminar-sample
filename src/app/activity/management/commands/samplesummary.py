import random
from datetime import date, datetime, timedelta

from django.core import management
from django.core.management import BaseCommand, CommandParser

from app.activity.models import ActivityChoices, ActivitySummary, ArchivePeriod, EatChoices
from app.user.models import ServiceUser


class Command(BaseCommand):
    help = "テスト用にサンプルサマリー登録"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "--start",
            type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
            default=date(2000, 6, 3),
        )
        parser.add_argument(
            "--end",
            type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
            default=date(2024, 3, 13),
        )

    def handle(self, *args, **options):
        start_date = options["start"]  # type:date
        end_date = options["end"]  # type:date

        user_data = [
            # username, step_range, gym_rate, dental_rate, morning_rate, snack_rate, start, end
            ("itamin", (7000, 14000), 0.2, 0.1, 0.1, 0.1, None, None),
            ("miura", (6000, 13000), 0.5, 0.7, 0.7, 0.3, date(2001, 1, 27), date(2013, 10, 16)),
            ("sweets", (7000, 15000), 0.6, 0.6, 0.6, 0.9, date(2003, 10, 8), None),
            ("leon", (8000, 16000), 0.8, 0.8, 0.4, 0.7, date(2020, 10, 14), None),
            ("ramune", (4000, 10000), 0.9, 0.9, 0.1, 0.9, date(2003, 10, 8), None),
            ("ukyo", (5000, 12000), 0.4, 0.9, 0.8, 0.8, None, None),
            ("kame", (12000, 23000), 0.7, 0.7, 0.8, 0.5, None, date(2008, 12, 17)),
            ("kame", (12000, 23000), 0.7, 0.7, 0.8, 0.5, date(2022, 10, 12), None),
        ]
        user_id_map = {
            user.username: user.id
            for user in ServiceUser.objects.filter(username__in=[username for username, *_ in user_data])
        }

        def flush():
            count = 0
            if summaries:
                count = len(ActivitySummary.objects.bulk_create(summaries))
                summaries.clear()
            return count

        summaries = []
        saved_count = 0
        dt = start_date
        while dt <= end_date:
            for username, step_range, gym_rate, dental_rate, morning_rate, snack_rate, start, end in user_data:
                if (start and dt < start) or (end and dt > end):
                    continue
                summaries.append(
                    ActivitySummary(
                        target_date=dt,
                        user_id=user_id_map[username],
                        steps=random.randint(*step_range),
                        sleep_time=random.randint(30, 80) / 10,
                        gymnastics=ActivityChoices.DONE if random.random() < gym_rate else ActivityChoices.NOT,
                        dental=ActivityChoices.DONE if random.random() < dental_rate else ActivityChoices.NOT,
                        morning=EatChoices.EAT if random.random() < morning_rate else EatChoices.NOT,
                        snack=EatChoices.EAT if random.random() < snack_rate else EatChoices.NOT,
                    )
                )
            dt += timedelta(days=1)

            if len(summaries) > 1000:
                saved_count += flush()
                print("saved", saved_count, end="\r")

        saved_count += flush()
        print("saved", saved_count)

        # 週次アーカイブ
        print("weekly archive")
        dt = start_date - timedelta(days=start_date.weekday())
        while dt + timedelta(days=6) <= end_date:
            print(dt, end="\r")
            management.call_command("archiveactivity", date=dt, period=ArchivePeriod.WEEKLY)
            dt += timedelta(days=7)

        # 月次アーカイブ
        print("monthly archive")
        dt = start_date.replace(day=1)
        while dt.strftime("%Y-%m") < end_date.strftime("%Y-%m"):
            print(dt, end="\r")
            management.call_command("archiveactivity", date=dt, period=ArchivePeriod.MONTHLY)
            dt = (dt + timedelta(days=40)).replace(day=1)

        # 年次アーカイブ
        print("annual archive")
        dt = start_date.replace(month=1, day=1)
        while dt.year < end_date.year:
            print(dt, end="\r")
            management.call_command("archiveactivity", date=dt, period=ArchivePeriod.ANNUAL)
            dt = dt.replace(year=dt.year + 1)
