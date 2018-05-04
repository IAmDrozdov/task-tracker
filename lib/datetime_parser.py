import re
from datetime import datetime

from lib.constants import Constants as const


def get_deadline(deadline_string):
    """
    Parse string like to datetime object
    :param deadline_string: string in format "DAY MONTH"
    :return: string in datetime format
    """
    input_format = '%d %B%Y'
    curr_year_input = datetime.strptime(deadline_string + str(datetime.now().year), input_format)
    if curr_year_input < datetime.now():
        return str(datetime.strptime(deadline_string + str(datetime.now().year + 1), input_format))
    else:
        return str(curr_year_input)


def parse_iso_pretty(date_iso):
    """
    PArse iso-like date to human-like
    :param date_iso: date in iso-like format
    :return: human-like formated date like "DAY MONTH"
    """
    return parse_iso(date_iso).strftime('%d %b')


def parse_iso(date_iso):
    """
    Parse iso-like date to datetime object
    :param date_iso:
    :return:
    """
    return datetime.strptime(date_iso, const.DATE_PATTERN).date()


def get_first_weekday(month, year):
    """
    Get first weekday of this month
    :param month: month to show
    :param year: year to show
    :return: int value [1..7]
    """
    string_date = str(month) + str(year)
    date_datetime = datetime.strptime('1' + string_date, '%d%m%Y')
    return date_datetime.weekday() + 1


def get_weekday_number(str_weekday):
    """
    Using name of weekday return its number representation
    :param str_weekday: weekday from mon - sun
    :return: integer number [0..7]
    """
    weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    return weekdays.index(str_weekday[:3].lower())


def get_weekday_word(number):
    """
    Using weekday index return its word representation
    :param number: number of weekday [0..6]
    :return: word representation
    """
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return weekdays[number]


def parse_period(period):
    """
    parse period  for plans.
    :param period: integer value or list of weekdays
    :return: dict with type and value for period
    """
    if period.isdigit():
        return {'period': int(period), 'type': const.REPEAT_DAY}
    else:
        weekdays_digits_list = []
        weekdays_list = re.split("[^\w]", period)
        for day in weekdays_list:
            weekdays_digits_list.append(get_weekday_number(day))
        return {'period': weekdays_digits_list, 'type': const.REPEAT_WEEKDAY}


def parse_time(string_time):
    """
    Parse time for plans.
    :param string_time: time in format HH:MM or only HH
    :return: depending on param return dict with type and value of time
    """
    if ':' in string_time:
        hm_time = {'hour': int(string_time.split(':')[0]), 'minutes': int(string_time.split(':')[1]),
                   'with_minutes': True}
        if hm_time['hour'] > 24 or hm_time['hour'] < 0 or hm_time['minutes'] > 60 or hm_time['minutes'] < 0:
            raise ValueError
        return hm_time
    else:
        return {'hour': int(string_time), 'with_minutes': False}


def is_match(task, month, year):
    """
    Comparing this month and year with task deadline date
    :param self: task obgect
    :param month: month to compare
    :param year: year to compare
    :return: True if all is good else False
    """
    if task.deadline:
        return True if parse_iso(task.deadline).month == month and \
                       parse_iso(task.deadline).year == year else False
    else:
        return False


def mark_dates(tasks, month, year):
    """
    If task deadline coincides with this month and year this task day of deadline appends to list
    :param tasks: list of tasks
    :param month: month to compare
    :param year:year to compare
    :return: list of dates what coincided
    """
    marked_dates = []
    for task in tasks:
        if is_match(task, month, year):
            new_day = parse_iso(task.deadline).day
            if new_day not in marked_dates:
                marked_dates.append(new_day)
    return marked_dates
