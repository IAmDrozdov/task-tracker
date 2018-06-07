from django.core.wsgi import get_wsgi_application
import os


def configure(settings_module="calelib.database_settings.settings"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    get_wsgi_application()
