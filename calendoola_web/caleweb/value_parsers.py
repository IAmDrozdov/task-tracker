from calelib.constants import Constants


def get_month(month):
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
    return months.index(month.lower()) + 1 if type(month) == str else months[month - 1]


def get_weekday(weekday):
    weekdays = (
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
    )
    return weekdays.index(weekday.lower()) if type(weekday) == str else weekdays[weekday]


def parse_period(period_type, period_value):
    parsed_period = {}
    if period_type == Constants.REPEAT_DAY:
        parsed_period = {'day': int(period_value)}
    elif period_type == Constants.REPEAT_WEEKDAY:
        weekdays_list = period_value.strip().split()
        weekdays_digits_list = [get_weekday(day) for day in weekdays_list]
        parsed_period = {'days': list(set(weekdays_digits_list))}
    elif period_type == Constants.REPEAT_MONTH:
        period_value = period_value.strip().split()
        month_list = period_value[1:]
        month_digits_list = [get_month(month) for month in month_list]
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


def parse_period_to_view(period_type, period_value):
    if period_type == Constants.REPEAT_DAY:
        return period_value['day']
    elif period_type == Constants.REPEAT_WEEKDAY:
        return ', '.join([get_weekday(e) for e in period_value['days']])
    else:
        return '{} {}'.format(period_value['day'], ' '.join([get_month(e) for e in period_value['months']]))
