from django import template
from calelib.constants import Constants

register = template.Library()


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


@register.filter(name='humanize_period')
def word_months(period, type):
    if type == Constants.REPEAT_MONTH:
        return 'Every {}th of {}'.format(period['day'],
                                         ', '.join([get_month_word(e).capitalize() for e in period['months']]))
    elif type == Constants.REPEAT_DAY:
        if period['day'] > 1:
            return 'Every {} days'.format(period['day'])
        else:
            return 'Every day'
    elif type == Constants.REPEAT_WEEKDAY:
        return 'Every {}'.format(', '.join([get_weekday_word(e).capitalize() for e in period['days']]))
