from datetime import datetime, timedelta
from src.settings import TIMEZONE


def get_oci_datetime_kwargs():
    return {
        'hour': 0,
        'minute': 0,
        'second': 0,
        'microsecond': 0,
        'tzinfo': TIMEZONE
    }

def get_now() -> datetime:
    return datetime.now(TIMEZONE)

def get_current_month() -> str:
    return get_now().strftime('%m/%Y')

def get_current_month_start_datetime() -> datetime:
    return get_now().replace(day=1, **get_oci_datetime_kwargs())

def get_current_month_end_datetime() -> datetime:
    return (get_now() + timedelta(days=1)).replace(**get_oci_datetime_kwargs())
