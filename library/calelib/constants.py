from typing import NamedTuple


class _Constants(NamedTuple):
    """General constants for reminders and plans"""
    REPEAT_DAY: '_Constants' = 'd'
    REPEAT_WEEKDAY: '_Constants' = 'wd'
    REPEAT_MONTH: '_Constants' = 'm'
    REPEAT_YEAR: '_Constants' = 'y'
    REMIND_MINUTES: '_Constants' = 'm'
    REMIND_HOURS: '_Constants' = 'h'
    REMIND_DAYS: '_Constants' = 'd'
    REMIND_MONTHS: '_Constants' = 'mth'


class _Status(NamedTuple):
    """General statuses for tasks"""
    FINISHED: '_Status' = 'Finished'
    UNFINISHED: '_Status' = 'Not finished'
    OVERDUE: '_Status' = 'Overdue'


class _Notifications(NamedTuple):
    """General notification types"""
    OVERDUE = 'Overdue task'
    PLANNED = 'Created planned task'
    REMOVED = 'Removed planned task'
    REMIND = 'Reminding'


Status = _Status()
Constants = _Constants()
Notifications = _Notifications()
