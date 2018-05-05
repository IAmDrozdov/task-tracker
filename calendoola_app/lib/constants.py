from calendoola_app.lib.config import Config


class Constants:
    """
    Project constants
    """
    config = Config('config.ini')
    PID_PATH_FILE = config.get_config_field('pid')
    STATUS_FINISHED = 'FINISHED'
    STATUS_UNFINISHED = 'UNFINISHED'
    DATE_PATTERN = "%Y-%m-%d %H:%M:%S"
    REPEAT_DAY = 'd'
    REPEAT_WEEKDAY = 'wd'
    DELIMITERS = ['_', '|', '#', '+', '.']
    try:
        ID_DELIMITER = DELIMITERS[int(config.get_config_field('delimiter'))]
    except IndexError:
        ID_DELIMITER = DELIMITERS[0]
    DATABASE_PATH = config.get_config_field('database')
    LOGGING_PATH = config.get_config_field('logger_output')
