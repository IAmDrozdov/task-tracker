import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from .config import Config
from .constants import Constants, Status
from .crud import Database
from .daemon import Daemon
from .custom_exceptions import (DaemonIsNotStarted,
                                DaemonAlreadyStarted,
                                CycleError
                                )
from .notification import call
import logging


def configure_logger(path, log_format, level):
    clogger = logging.getLogger('calendoola_logger')
    handler = logging.FileHandler(path)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    clogger.addHandler(handler)
    clogger.setLevel(getattr(logging, level))
