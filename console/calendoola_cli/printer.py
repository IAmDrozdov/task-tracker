import calendar

import date_parse as dp
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
    created = 'created' if plan.created else 'not created'
    time = plan.time_at if plan.time_at else 'No time'
    print(
        'ID: {}\nStatus: {}\nInfo: {}\nType: {}\nDate: {} Time:{}'.format(plan.id, created, plan.info, plan.period_type,
                                                                          plan.period, time))


def print_plans(plans, colored):
    for plan in plans:
        if colored:
            color = Fore.LIGHTCYAN_EX if plan.created else Fore.RED
        else:
            color = Fore.RESET
        print(color + '|ID {}| {}'.format(plan.id, plan.info))


def print_reminder(reminder):
    tasks = ', '.join([t.id for t in reminder.tasks.all()]) if reminder.tasks.all().exists() else 'No tasks'
    print('ID : {}\nTasks: {}\nReminding: {}'.format(reminder.id, tasks, reminder))


def print_reminders(reminders):
    for reminder in reminders:
        print('ID: {} | {}'.format(reminder.id, reminder))
