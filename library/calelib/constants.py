from typing import NamedTuple


class _Constants(NamedTuple):
    REPEAT_DAY: '_Constants' = 'd'
    REPEAT_WEEKDAY: '_Constants' = 'wd'
    REPEAT_MONTH: '_Constants' = 'm'
    REPEAT_YEAR: '_Constants' = 'y'
    REMIND_MINUTES: '_Constants' = 'm'
    REMIND_HOURS: '_Constants' = 'h'
    REMIND_DAYS: '_Constants' = 'd'
    REMIND_MONTHS: '_Constants' = 'mth'


class _Status(NamedTuple):
    FINISHED: '_Status' = 'Finished'
    UNFINISHED: '_Status' = 'Not finished'
    OVERDUE: '_Status' = 'Overdue'


Status = _Status()
Constants = _Constants()
