import calendar
import datetime_parser
from colorama import Fore, Back


def is_match(self, month, year):
    if self['deadline'] is not None:
        formated = datetime_parser.parse_date(self['deadline'])
    else:
        return False
    if formated.month == month and formated.year == year:
        return True
    else:
        return False


def print_month_calendar(container, month, year):
    cal = calendar.Calendar()
    marked_dates = []
    first_day = datetime_parser.get_day(month, year)
    day_counter = 0
    for task in container:
        if is_match(task, month, year):
            new_day = datetime_parser.parse_date(task['deadline']).day
            if new_day not in marked_dates:
                marked_dates.append(new_day)

    print(Back.LIGHTWHITE_EX + 'Mon Tue Wed Thu Fri Sat Sun' + Back.RESET)
    for i in range(1, first_day+1):
        if i != first_day:
            print('   ', end=' ')
        day_counter = day_counter + 1
    else:
        print(' ', end='')
    for day in cal.itermonthdays(month, month):
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
