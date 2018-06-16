from django import template

register = template.Library()


@register.filter(name='colorize')
def priority_div_months(priority):
    COLORS = ['#92c17b',
              '#afd19e',
              '#d1c09e',
              '#c17b92',
              '#a34d69']

    return COLORS[priority - 1]
