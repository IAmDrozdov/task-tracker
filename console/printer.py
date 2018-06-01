import calendar
from datetime import datetime

import date_parse as dp
from calelib import Constants
from colorama import Fore, Back


def print_user(user):
    tasks_print = []
    plans_print = []
    if user.tasks.all().exists():
        for task in user.tasks.all():
            tasks_print.append(task.info)
        tasks_print = 'tasks:\n' + ', '.join(tasks_print)
    else:
        tasks_print = 'No tasks'

    if user.plans.all().exists():
        for plan in user.plans.all():
            plans_print.append(plan.info)
        plans_print = 'plans:\n' + ', '.join(plans_print)
    else:
        plans_print = 'No plans'
    print('user: {}\n{}\n{}'.format(user.nickname, tasks_print, plans_print))


def _short_print_task(task, priority_colors):
    subtasks_print = '' if '(' + str(task.subtasks.all().count) + ')' else task.subtasks.all().exist()
    print(priority_colors[task.priority - 1] + 'ID: {} | {} {}'.format(task.id, task.info, subtasks_print))


def print_task(tasks, colored, tags=None):
    if colored:
        priority_colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.LIGHTMAGENTA_EX, Fore.RED]
    else:
        priority_colors = [Fore.RESET] * 6
    for task in tasks:
        if tags:
            if all(elem in task.tags for elem in tags):
                _short_print_task(task, priority_colors)
            print_task(task.subtasks.all(), colored, tags=tags)
        else:
            _short_print_task(task, priority_colors)


def print_main_task(task):
    deadline_print = dp.parse_iso_pretty(task.deadline) if task.deadline else 'No deadline'
    tags_print = ', '.join(task.tags) if len(task.tags) > 0 else 'No tags'
    print('Information: {}\nID: {}\nDeadline: {}\nStatus: {}\nPriority: {}\nCreated: {}\nLast change: {}\nTags: {}'
          .format(task.info, task.id, deadline_print, task.status, task.priority,
                  dp.parse_iso_pretty(task.created_at), dp.parse_iso_pretty(task.updated_at), tags_print))

    if task.subtasks.all().exists():
        print('Subtasks:')
        print_task(task.subtasks.all(), False)
    else:
        print('No subtasks')


def print_calendar(tasks, month, year):
    cal = calendar.Calendar()
    for _ in cal.itermonthdays(year, month):
        pass
    marked_dates = dp.mark_dates(tasks, month, year)
    first_day = dp.get_first_weekday(month, year)
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


def print_plan(plan):
    created = 'Status: created' if plan.is_created else 'Status: not created'
    period_print = 'Period: every '
    time_print = 'in ' + plan.time_at + " o'clock" if plan.time_at else ''
    next_print = 'Next creating: '
    if plan.period_type == Constants.REPEAT_DAY:
        period_print += str(plan.period) + ' days'
        next_print += dp.parse_iso_pretty(plan.next_create)
    else:
        weekdays = []
        for day in plan.period:
            weekdays.append(dp.get_weekday_word(day))
        period_print += ', '.join(weekdays)
        if len(plan.period) > 1:
            next_print += dp.get_weekday_word(
                min(filter(lambda x: x > datetime.now().weekday(), plan.period)))
        else:
            next_print += dp.get_weekday_word(plan.period[0])
    print('Information: {}\n{}\nID: {}\n{}\n{} {}'
          .format(plan.info, created, plan.id, next_print, period_print, time_print))


def print_plans(plans, colored):
    for plan in plans:
        if colored:
            color = Fore.LIGHTCYAN_EX if plan.is_created else Fore.RED
        else:
            color = Fore.RESET
        print(color + '|ID {}| {}'.format(plan.id, plan.info))
