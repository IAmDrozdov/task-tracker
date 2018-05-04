from lib.config import Config


class Constants:
    """
    Project constants
    """
    config = Config('config.ini')
    PID_PATH_FILE = config.get_config_field('pid')
    STATUS_FINISHED = config.get_config_field('status_finished')
    STATUS_UNFINISHED = config.get_config_field('status_unfinished')
    DATE_PATTERN = "%Y-%m-%d %H:%M:%S"
    REPEAT_DAY = 'd'
    REPEAT_WEEKDAY = 'wd'
    ID_DELIMITER = config.get_config_field('delimiter')
    DATABASE_PATH = config.get_config_field('database')
    LOGGING_PATH = config.get_config_field('logger_output')
