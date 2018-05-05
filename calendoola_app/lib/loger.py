import logging, logging.config
from calendoola_app.lib.constants import Constants as const


def logger():
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        filename=const.LOGGING_PATH,
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    return logger
