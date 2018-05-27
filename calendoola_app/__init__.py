import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def configure_logger(path, log_format, level):
    logger = logging.getLogger('calendoola_logger')
    handler = logging.FileHandler(path)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level))
