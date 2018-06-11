from django import template
from calelib.config import Config
from calelib.constants import Constants
register = template.Library()


@register.simple_tag(name='current_user')
def current():
    cfg = Config(Constants.CONFIG_FILE_PATH)
    return cfg.get_config_field('current_user').upper()
