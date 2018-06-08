import os

from django.core.wsgi import get_wsgi_application


def configure_database(settings_module="calelib.database_settings.settings"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    get_wsgi_application()
