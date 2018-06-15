from calelib.constants import Constants


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


def parse_period(period_type, period_value):
    """
    parse entered period in period what can understand "plan"
    :param period_type: type of periodic
    :param period_value: date of period
    :return: dict of readable for plan data for creating tasks
    """

    parsed_period = {}
    if period_type == Constants.REPEAT_DAY:
        parsed_period = {'day': int(period_value)}
    elif period_type == Constants.REPEAT_WEEKDAY:
        weekdays_list = period_value.strip().split()
        weekdays_digits_list = [get_weekday_number(day) for day in weekdays_list]
        parsed_period = {'days': list(set(weekdays_digits_list))}
    elif period_type == Constants.REPEAT_MONTH:
        period_value = period_value.strip().split()
        month_list = period_value[1:]
        month_digits_list = [get_month_number(month) for month in month_list]
        parsed_period = {
            'months': list(set(month_digits_list)),
            'day': int(period_value[0])
        }

    return parsed_period


def parse_remind_type(string_type):
    if string_type == 'min':
        return Constants.REMIND_MINUTES
    elif string_type == 'hour':
        return Constants.REMIND_HOURS
    elif string_type == 'day':
        return Constants.REMIND_DAYS
    else:
        return Constants.REMIND_MONTHS
