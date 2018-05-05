from datetime import datetime
import re


def get_deadline(deadline_string):
    curr_year_input = datetime.strptime(deadline_string + str(datetime.now().year), '%d %B%Y')
    if curr_year_input < datetime.now():
        return str(datetime.strptime(deadline_string + str(datetime.now().year+1), '%d %B%Y'))
    else:
        return str(curr_year_input)


def parse_iso_pretty(date_iso):
    try:
        return date_iso.strftime('%d %b')
    except AttributeError:
        return parse_iso(date_iso).strftime('%d %b')


def parse_iso(date_iso):
    return datetime.strptime(date_iso, "%Y-%m-%d %H:%M:%S").date()


def get_first_weekday(month, year):
    string_date = str(month) + str(year)
    date_datetime = datetime.strptime('1' + string_date, '%d%m%Y')
    return date_datetime.weekday() + 1


def get_weekday(str_weekday):
    weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    return weekdays.index(str_weekday[:3].lower())


def parse_period(period):
    if period.isdigit():
        return [int(period), 'd']
    else:
        weekdays_digits_list = []
        weekdays_list = re.sub("[^\w]", " ", period).split()
        for day in weekdays_list:
            weekdays_digits_list.append(get_weekday(day))
        return [weekdays_digits_list, 'wd']

