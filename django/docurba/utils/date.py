from datetime import date, datetime, time

from django.utils import timezone


def end_of_day(value: date) -> datetime:
    return datetime.combine(value, time.max, tzinfo=timezone.get_default_timezone())
