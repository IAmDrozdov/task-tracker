import logging

from .db.database import Database
from .etc.custom_exceptions import (UserNotAuthorized, UserNotFound, UserAlreadyExists, TaskNotFound, PlanNotFound,
                                    CycleError, DaemonIsNotStarted, DaemonAlreadyStarted)
from .etc.daemon import Daemon
from .models.plan import Plan
from .models.task import Task
from .models.user import User
from .modules.config import Config
from .modules.constants import Status, Constants
from .modules.logger import logg
from .modules.notification import call


def configure_logger(path, log_format, level):
    clogger = logging.getLogger('calendoola_logger')
    handler = logging.FileHandler(path)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    clogger.addHandler(handler)
    clogger.setLevel(getattr(logging, level))
