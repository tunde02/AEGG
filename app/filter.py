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
        ('Cast:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">Cast :</strong>'),
        ('Recall:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">Recall :</strong>'),
        ('OR', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">OR</strong>'),
        ('Link', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">Link</strong>'),
        ('Echo', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">Echo</strong>'),
        ('Attach', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">Attach</strong>'),
        ('부착', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">부착</strong>'),
        ('Immediately:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">IMMEDIATELY :</strong>'),
        ('Persistent:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">PERSISTENT :</strong>'),
        ('To Discard:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">TO DISCARD :</strong>'),
        ('Power 1:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">POWER 1 :</strong>'),
        ('Power 2:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">POWER 2 :</strong>'),
        ('Power 3:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">POWER 3 :</strong>'),
        ('Power 4:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">POWER 4 :</strong>'),
        ('Power 5:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">POWER 5 :</strong>'),
        ('Power 6:', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">POWER 6 :</strong>'),
        ('Power', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">Power</strong>'),
        ('Attack', '<strong style="font: 1.1em \'빛의 계승자 Bold\';">Attack</strong>'),
        ('\r\n---\r\n', '<strong class="d-flex border-bottom border-3 border-dark my-3"></strong>'),
        ('\r\n', '<br>')
    ]

    for before, after in replace_rules:
        replaced = replaced.replace(before, after)

    return replaced
