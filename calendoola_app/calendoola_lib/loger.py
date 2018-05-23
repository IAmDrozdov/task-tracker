import logging
import logging.config


def logger(path, level):
    """
    Set up from logger
    :param path: logging file path
    :param level: level of logging
    """
    if level == 'debug':
        logging_level = logging.DEBUG
    elif level == 'error':
        logging_level = logging.ERROR
    else:
        logging_level = logging.NOTSET

    logging.basicConfig(format='%(asctime)s [%(levelname)s] LOG: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        filename=path,
                        level=logging_level)
    logger = logging.getLogger(__name__)
    return logger
