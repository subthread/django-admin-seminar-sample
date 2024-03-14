from datetime import datetime, time, timedelta

from django.utils import timezone


def make_today():
    return datetime.combine(timezone.localdate(), time(), timezone.get_current_timezone())


def make_tomorrow():
    return make_today() + timedelta(1)
