from calendoola_app.lib.config import Config


class Constants:
    """
    Project constants
    """
    CONFIG_FILE_PATH = 'config.ini'
    config = Config(CONFIG_FILE_PATH)
    DATE_PATTERN = "%Y-%m-%d %H:%M:%S"
    REPEAT_DAY = 'd'
    REPEAT_WEEKDAY = 'wd'
    ID_DELIMITER = "_"
    LOGGING_PATH = config.get_config_field('logger_output_path')


class Status:
    FINISHED = 'FINISHED'
    UNFINISHED = 'UNFINISHED'
    OVERDUE = 'OVERDUE'
