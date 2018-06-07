import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calelib.database_settings.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from .config import Config
from .constants import Constants, Status
from .crud import Calendoola
from .custom_exceptions import (DaemonIsNotStarted,
                                DaemonAlreadyStarted,
                                CycleError
                                )
from .notification import call
