import os

from django.core.wsgi import get_wsgi_application


def configure_database(settings_module="calelib.database_settings.settings"):
    """
    Configure database with any settings
    Args:
        settings_module(str): path to settings file
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    get_wsgi_application()
