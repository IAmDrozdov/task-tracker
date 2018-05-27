class Constants:
    """
    Project constants
    """
    CONFIG_FILE_PATH = 'config.ini'
    DATE_PATTERN = "%Y-%m-%d %H:%M:%S"
    REPEAT_DAY = 'd'
    REPEAT_WEEKDAY = 'wd'
    REPEAT_MONTH = 'm'
    REPEAT_YEAR = 'y'
    ID_DELIMITER = "_"


class Status:
    """
    Tasks statuses
    """
    FINISHED = 'FINISHED'
    UNFINISHED = 'UNFINISHED'
    OVERDUE = 'OVERDUE'
