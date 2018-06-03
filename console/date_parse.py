from datetime import datetime

from calelib import Constants


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
    return date_iso.strftime('%d %b')


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


def get_month_number(str_month):
    months = (
        'jan',
        'feb',
        'mar',
        'apr',
        'may',
        'jun',
        'jul',
        'aug',
        'sep',
        'oct',
        'nov',
        'dec'
    )
    return months.index(str_month[:3].lower()) + 1


def get_month_word(number):
    months = (
        'january',
        'february',
        'march',
        'april',
        'may',
        'june',
        'july',
        'august',
        'september',
        'october',
        'november',
        'december'
    )
    return months[number - 1]


def get_weekday_number(str_weekday):
    """
    Using name of weekday return its number representation
    :param str_weekday: weekday from mon - sun
    :return: integer number [0..7]
    """
    weekdays = (
        'mon',
        'tue',
        'wed',
        'thu',
        'fri',
        'sat',
        'sun'
    )
    return weekdays.index(str_weekday[:3].lower())


def get_weekday_word(number):
    """
    Using weekday index return its word representation
    :param number: number of weekday [0..6]
    :return: word representation
    """
    weekdays = (
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
    )
    return weekdays[number]


def parse_period(period_type, period_value):
    """
    parse entered period in period what can understand "plan"
    :param period_type: type of periodic
    :param period_value: date of period
    :return: dict of readable for plan data for creating tasks
    """
    parsed = {'period': None, 'type': None}
    if period_type == 'day':
        parsed['period'] = {'day': int(period_value)}
        parsed['type'] = Constants.REPEAT_DAY
    elif period_type == 'week':
        weekdays_list = period_value.strip().split()
        weekdays_digits_list = [get_weekday_number(day) for day in weekdays_list]
        parsed['period'] = {'days': list(set(weekdays_digits_list))}
        parsed['type'] = Constants.REPEAT_WEEKDAY
    elif period_type == 'month':
        period_value = period_value.strip().split()
        month_list = period_value[1:]
        month_digits_list = [get_month_number(month) for month in month_list]
        parsed['period'] = {
            'months': list(set(month_digits_list)),
            'day': int(period_value[0])
        }
        parsed['type'] = Constants.REPEAT_MONTH
    elif period_type == 'year':
        period_value = period_value.strip().split()
        parsed['type'] = Constants.REPEAT_YEAR
        parsed['period'] = {
            'day': int(period_value[0]),
            'month': get_month_number(period_value[1])
        }
    return parsed['type'], parsed['period']


def parse_time(string_time):
    """
    Parse time for plans.
    :param string_time: time in format HH:MM or only HH
    :return: depending on param return dict with type and value of time
    """
    hm_time = {'hour': None,
               'minutes': None,
               'with_minutes': None
               }
    if ':' in string_time:
        hm_time['hour'] = int(string_time.split(':')[0])
        hm_time['minutes'] = int(string_time.split(':')[1])
        hm_time['with_minutes'] = True
        if hm_time['hour'] > 24 or hm_time['hour'] < 0 or hm_time['minutes'] > 60 or hm_time['minutes'] < 0:
            raise ValueError

    else:
        hm_time['hour'] = int(string_time)
        hm_time['with_minutes'] = False
    return hm_time


def parse_remind_type(string_type):
    if string_type == 'min':
        return Constants.REMIND_MINUTES
    elif string_type == 'hour':
        return Constants.REMIND_HOURS
    elif string_type == 'day':
        return Constants.REMIND_DAYS
    else:
        return Constants.REMIND_MONTHS
