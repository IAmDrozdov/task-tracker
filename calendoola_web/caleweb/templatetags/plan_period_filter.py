from django import template

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
    if type == 'm':
        return 'Every {}th of {}'.format(period['day'],
                                         ', '.join([get_month_word(e).capitalize() for e in period['months']]))
    elif type == 'd':
        not_plural = 'Every {} day'.format(period['day'])
        if period['day'] > 1:
            return not_plural + 's'
        else:
            return not_plural
    elif type == 'wd':
        return 'Every {}'.format(', '.join([get_weekday_word(e).capitalize() for e in period['days']]))
    else:
        return 'Every year on {} {}'.format(get_month_word(period['month']), period['day'])
