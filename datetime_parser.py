from datetime import datetime


def get_deadline(deadline_string):
    return datetime.strptime(deadline_string + str(datetime.now().year), '%d %B%Y')


def parse_date(date_iso):
    return datetime.strptime(date_iso, "%Y-%m-%dT%H:%M:%SZ")


def date_print(date_iso):
    return parse_date(date_iso).strftime('%d.%m.%Y')


def get_day(month, year):
    string_date = str(month) + str(year)
    date_datetime = datetime.strptime('1' + string_date, '%d%m%Y')
    return date_datetime.weekday() + 1

