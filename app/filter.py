from datetime import datetime
from babel.dates import format_datetime


def datetime_format(value):
    if datetime.now().day == value.day:
        return format_datetime(value, 'HH:mm')
    else:
        return format_datetime(value, 'MM-dd')


def datetime_detail_format(value):
    return format_datetime(value, 'yyyy.MM.dd HH:mm:ss')


def replace_keywords_format(value):
    replaced = value
    replace_rules = [
        ('에테르 ', '<img class="mb-1 me-2" src="/static/images/defaults/aether.png" width="18" height="18">'),
        ('에테르', '<img class="mb-1 me-2" src="/static/images/defaults/aether.png" width="18" height="18">'),
        ('Aether ', '<img class="mb-1 me-2" src="/static/images/defaults/aether.png" width="18" height="18">'),
        ('Aether', '<img class="mb-1 me-2" src="/static/images/defaults/aether.png" width="18" height="18">'),
        ('Cast:', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">Cast :</strong>'),
        ('Recall:', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">Recall :</strong>'),
        ('OR', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">OR</strong>'),
        ('Link', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">Link</strong>'),
        ('Echo', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">Echo</strong>'),
        ('Attach', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">Attach</strong>'),
        ('부착', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">부착</strong>'),
        ('IMMEDIATELY', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">IMMEDIATELY</strong>'),
        ('PERSISTENT', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">PERSISTENT</strong>'),
        ('TO DISCARD', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">TO DISCARD</strong>'),
        ('POWER', '<strong style="font: 1.2em \'빛의 계승자 Bold\';">POWER</strong>'),
        ('\r\n---\r\n', '<strong class="d-flex border-bottom border-3 border-dark my-3"></strong>'),
        ('\r\n', '<br>'),
    ]

    for before, after in replace_rules:
        replaced = replaced.replace(before, after)

    return replaced
