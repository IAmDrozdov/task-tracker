import calendar
import datetime_parser


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
    container_date_collection = []
    marked_dates = []
    day_counter = 0
    print(cal.firstweekday)
    for task in container:
        if is_match(task, month, year):
            container_date_collection.append(datetime_parser.parse_date(task['deadline']))
    for day in cal.itermonthdays(month, month):
        if (day_counter % 7) == 0:
            print(day)
        else:
            print('{num:02d}'.format(num=day), end=' ')
        day_counter = day_counter + 1

        for day_in_collection in container_date_collection:
            if day == day_in_collection.day:
                if day not in marked_dates:
                    marked_dates.append(day)


############# get weekady as string
############# parse string to int
############# start printing with day_counter = 0 -> int