import calendar
import copy
import re
import time
from datetime import datetime

from colorama import Fore, Back

import lib.daemon as daemon
from lib import datetime_parser as dp
from lib.constants import Constants as const
from lib.database import Database
from lib.plan import Plan
from lib.task import Task
from lib.user import User


def operation_user_add(db, nickname, force):
    db.add_user(User(nickname=nickname))
    if force:
        db.set_current_user(nickname)


def operation_user_login(db, nickname):
    db.set_current_user(nickname)


def operation_user_logout(db):
    db.remove_current_user()


def operation_user_remove(db, nickname):
    db.remove_user(nickname)


def operation_user_info(db):
    user = db.get_current_user()
    tasks_print = []
    plans_print = []
    if user.tasks:
        for task in user.tasks:
            tasks_print.append(task.info)
        tasks_print = 'tasks:\n' + ', '.join(tasks_print)
    else:
        tasks_print = 'No tasks'

    if user.plans:
        for plan in user.plans:
            plans_print.append(plan.info)
        plans_print = 'plans:\n' + ', '.join(plans_print)
    else:
        plans_print = 'No plans'
    print('user: {}\n{}\n{}'.format(user.nickname, tasks_print, plans_print))


def operation_task_add(db, description, priority, deadline, tags, subtask):
    db.add_task(Task(info=description, priority=priority if priority else 1,
                     deadline=dp.get_deadline(deadline) if deadline else None,
                     tags=re.split("[^\w]", tags) if tags else [],
                     parent_id=subtask))


def operation_task_remove(db, id):
    db.remove_task(id)


def task_print(tasks, colored, short=True, tags=None):
    if colored:
        priority_colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.LIGHTMAGENTA_EX, Fore.RED]
    else:
        priority_colors = [Fore.RESET] * 6

    for task in tasks:
        if tags:
            if all(elem in task.tags for elem in re.split("[^\w]", tags)):
                subtasks_print = '' if len(task.subtasks) == 0 else '(' + str(len(task.subtasks)) + ')'
                print(priority_colors[task.priority - 1] + 'ID: {} | {} {}'.format(task.id, task.info, subtasks_print))
            task_print(task.subtasks, colored, tags=tags)
        elif short:
            subtasks_print = '' if len(task.subtasks) == 0 else '(' + str(len(task.subtasks)) + ')'
            print(priority_colors[task.priority - 1] + 'ID: {} | {} {}'.format(task.id, task.info, subtasks_print))
        elif not short:
            offset = '' if task.indent == 0 else task.indent * ' ' + task.indent * ' *'
            print(priority_colors[task.priority - 1] + offset + '| {} | {}'.format(task.id, task.info))
            task_print(task.subtasks, colored, False)


def operation_task_show(db, choice, selected, all, colored):
    if choice == 'id':
        task = db.get_tasks(selected)
        deadline_print = dp.parse_iso_pretty(task.deadline) if task.deadline else 'No deadline'
        tags_print = ', '.join(task.tags) if len(task.tags) > 0 else 'No tags'
        print('Information: {}\nID: {}\nDeadline: {}\nStatus: {}\nCreated: {}\nLast change: {}\nTags: {}'
              .format(task.info, task.id, deadline_print, task.status,
                      dp.parse_iso_pretty(task.date), dp.parse_iso_pretty(task.last_change), tags_print))
        print('Subtasks:')
        task_print(task.subtasks, colored)
    elif choice == 'tags':
        task_print(db.get_tasks(), colored, tags=selected)
    elif all:
        task_print(db.get_tasks(), colored, False)
    elif not choice:
        task_print(db.get_tasks(), colored)


def operation_task_finish(db, id):
    task_finish = db.get_tasks(id)
    if hasattr(task_finish, 'owner'):
        user_owner = db.get_users(task_finish.owner['nickname'])
        Database.get_task_by_id(user_owner.tasks, task_finish.owner['id'].split(const.ID_DELIMITER)).finish()
        user_owner.archive_task(task_finish.owner['id'])
    db.change_task(id, status=const.STATUS_FINISHED)
    db.get_current_user().archive_task(id)
    db.serialize()


def operation_task_move(db, id_from, id_to):
    task_from = db.get_tasks(id_from)
    task_to = db.get_tasks(id_to)
    task_to.append_task(copy.deepcopy(task_from))
    db.remove_task(id_from)


def operation_task_change(db, id, info, deadline, priority, status, append_tags, remove_tags):
    db.change_task(id, info=info, deadline=deadline, priority=priority, status=status, plus_tag=append_tags,
                   minus_tag=remove_tags)


def operation_task_share(db, id_from, nickname_to, delete, track):
    task_from = db.get_tasks(id_from)
    user_to = db.get_users(nickname_to)
    task_send = copy.deepcopy(task_from)
    task_send.id = Database.get_id(user_to.tasks)
    task_send.reset_sub_id()
    if track:
        task_send.owner = {'nickname': db.get_current_user().nickname, 'id': id_from}
    user_to.tasks.append(task_send)
    db.serialize()
    if delete:
        db.remove_task(id_from)


def operation_calendar_show(tasks, month, year):
    cal = calendar.Calendar()
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


def operation_plan_add(db, description, period, time):
    period_options = dp.parse_period(period)
    db.add_plan(Plan(info=description, period=period_options['period'],
                     period_type=period_options['type'],
                     time_at=dp.parse_time(time) if time else None))


def operation_plan_show(db, id, colored):
    if id:
        plan = db.get_plans(id)
        created = 'Status: created' if plan.is_created else 'Status: not created'
        period_print = 'Period: every '
        time_print = 'in ' + plan.time_at + " o'clock" if plan.time_at else ''
        next_print = 'Next creating: '
        if plan.period_type == const.REPEAT_DAY:
            period_print += str(plan.period) + ' days'
            next_print += dp.parse_iso_pretty(plan.next_create)
        else:
            weekdays = []
            for day in plan.period:
                weekdays.append(dp.get_weekday_word(day))
            period_print += ', '.join(weekdays)
            if len(plan.period) > 1:
                next_print += dp.get_weekday_word(min(filter(lambda x: x > datetime.now().weekday(), plan.period)))
            else:
                next_print += dp.get_weekday_word(plan.period[0])
        print('Information: {}\n{}\nID: {}\n{}\n{} {}'
              .format(plan.info, created, plan.id, next_print, period_print, time_print))
    else:
        for plan in db.get_plans():
            if colored:
                color = Fore.LIGHTCYAN_EX if plan.is_created else Fore.RED
            else:
                color = Fore.RESET
            print(color + '|ID {}| {}'.format(plan.id, plan.info))


def operation_plan_remove(db, id):
    db.remove_plan(id)


def check_plans(db):
    while True:
        for plan in db.get_plans():
            plan.check(db)
        time.sleep(10)


def run_daemon(db):
    daemon.run(check_plans, db)


def stop_daemon():
    daemon.stop()


def restart_daemon(db):
    daemon.restart(check_plans, db)
