from django import template
from django.template.defaultfilters import stringfilter

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


@register.filter
@stringfilter
def word_months(month_list):
    return [get_month_word(e) for e in month_list]


@register.filter
@stringfilter
def word_weekdays(weekdays_list):
    return [get_weekday_word(e) for e in weekdays_list]
