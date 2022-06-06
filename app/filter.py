from datetime import datetime
from babel.dates import format_datetime


def datetime_format(value):
    if datetime.now().day == value.day:
        return format_datetime(value, 'HH:mm')
    else:
        return format_datetime(value, 'MM-dd')


def datetime_detail_format(value):
    return format_datetime(value, 'yyyy.MM.dd HH:mm:ss')
