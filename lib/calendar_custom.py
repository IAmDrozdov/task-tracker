import calendar

from colorama import Fore, Back

from lib import datetime_parser


def is_match(self, month, year):
    if self.deadline:
        return True if datetime_parser.parse_iso(self.deadline).month == month and \
                       datetime_parser.parse_iso(self.deadline).year == year else False
    else:
        return False


def mark_dates(container, month, year):
    marked_dates = []
    for task in container:
        if is_match(task, month, year):
            new_day = datetime_parser.parse_iso(task.deadline).day
            if new_day not in marked_dates:
                marked_dates.append(new_day)
    return marked_dates


def print_month_calendar(container, month, year):
    cal = calendar.Calendar()
    marked_dates = mark_dates(container, month, year)
    first_day = datetime_parser.get_first_weekday(month, year)
    day_counter = 0

    print(Back.LIGHTWHITE_EX + 'Mon Tue Wed Thu Fri Sat Sun' + Back.RESET)
    for i in range(1, first_day + 1):
        if i != first_day:
            print('   ', end=' ')
        day_counter = day_counter + 1
    else:
        print(' ', end='')

    for day in cal.itermonthdays(year, month):
        task_foreground = Fore.WHITE
        if day in marked_dates:
            task_foreground = Fore.RED

        if day != 0:
            if (day_counter % 7) == 0:
                print(task_foreground + '{num:02d}'.format(num=day), end='\n ')
            else:
                print(task_foreground + '{num:02d}'.format(num=day), end='  ')
            day_counter = day_counter + 1
    else:
        print()
