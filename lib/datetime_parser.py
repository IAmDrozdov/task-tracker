import re
from datetime import datetime
from lib.constants import Constants as const


def get_deadline(deadline_string):
    input_format = '%d %B%Y'
    curr_year_input = datetime.strptime(deadline_string + str(datetime.now().year), input_format)
    if curr_year_input < datetime.now():
        return str(datetime.strptime(deadline_string + str(datetime.now().year + 1), input_format))
    else:
        return str(curr_year_input)


def parse_iso_pretty(date_iso):
    return parse_iso(date_iso).strftime('%d %b')


def parse_iso(date_iso):
    return datetime.strptime(date_iso, const.DATE_PATTERN).date()


def get_first_weekday(month, year):
    string_date = str(month) + str(year)
    date_datetime = datetime.strptime('1' + string_date, '%d%m%Y')
    return date_datetime.weekday() + 1


def get_weekday_number(str_weekday):
    weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    return weekdays.index(str_weekday[:3].lower())


def get_weekday_word(number):
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return weekdays[number]


def parse_period(period):
    if period.isdigit():
        return [int(period), const.REPEAT_DAY]
    else:
        weekdays_digits_list = []
        weekdays_list = re.sub("[^\w]", " ", period).split()
        for day in weekdays_list:
            weekdays_digits_list.append(get_weekday_number(day))
        return [weekdays_digits_list, const.REPEAT_WEEKDAY]


def parse_time(string_time):
    if ':' in string_time:
        return string_time.split(':')
    else:
        return string_time
