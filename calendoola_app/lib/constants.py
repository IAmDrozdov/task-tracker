from calendoola_app.lib.config import Config


class Constants:
    """
    Project constants
    """
    CONFIG_FILE_PATH = 'config.ini'
    config = Config(CONFIG_FILE_PATH)
    PID_PATH_FILE = config.get_config_field('pid')
    STATUS_FINISHED = 'FINISHED'
    STATUS_UNFINISHED = 'UNFINISHED'
    DATE_PATTERN = "%Y-%m-%d %H:%M:%S"
    REPEAT_DAY = 'd'
    REPEAT_WEEKDAY = 'wd'
    ID_DELIMITER = "_"
    DATABASE_PATH = config.get_config_field('database')
    LOGGING_PATH = config.get_config_field('logger_output')
