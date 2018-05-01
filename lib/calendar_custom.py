from lib import datetime_parser as dp


def is_match(self, month, year):
    if self.deadline:
        return True if dp.parse_iso(self.deadline).month == month and \
                       dp.parse_iso(self.deadline).year == year else False
    else:
        return False


def mark_dates(tasks, month, year):
    marked_dates = []
    for task in tasks:
        if is_match(task, month, year):
            new_day = dp.parse_iso(task.deadline).day
            if new_day not in marked_dates:
                marked_dates.append(new_day)
    return marked_dates
