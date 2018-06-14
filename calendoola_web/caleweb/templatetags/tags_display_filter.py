from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter(name='humanize_tags')
@stringfilter
def tags_output(tags_as_sting):
    return ', '.join(tags_as_sting.split())