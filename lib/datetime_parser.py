from datetime import datetime


def get_deadline(deadline_string):
    curr_year_input = datetime.strptime(deadline_string + str(datetime.now().year), '%d %B%Y')
    if curr_year_input < datetime.now():
        return str(datetime.strptime(deadline_string + str(datetime.now().year+1), '%d %B%Y'))
    else:
        return str(curr_year_input)


def parse_iso_pretty(date_iso):
    try:
        return date_iso.strftime('%d %b')
    except AttributeError:
        return datetime.strptime(date_iso, "%Y-%m-%d %H:%M:%S").strftime('%d %b')


def get_weekday(month, year):
    string_date = str(month) + str(year)
    date_datetime = datetime.strptime('1' + string_date, '%d%m%Y')
    return date_datetime.weekday() + 1
