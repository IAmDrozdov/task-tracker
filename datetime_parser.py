from datetime import datetime


def get_deadline(deadline_string):
    return datetime.strptime(deadline_string + str(datetime.now().year), '%d %B%Y')


def parse_date(date_iso):
    return datetime.strptime(date_iso, "%Y-%m-%dT%H:%M:%SZ")


def date_print(date_iso):
    return parse_date(date_iso).strftime('%d.%m.%Y')

