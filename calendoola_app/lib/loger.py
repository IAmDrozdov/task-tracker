import logging
import logging.config


def logger(path):
    logging.basicConfig(format='%(asctime)s [%(levelname)s] LOG: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        filename=path,
                        level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    return logger
