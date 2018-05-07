import calendar
import copy
import re
import time
from datetime import datetime

from colorama import Fore, Back

import calendoola_app.lib.custom_exceptions as ce
from calendoola_app.lib import datetime_parser as dp
from calendoola_app.lib.constants import Constants as const, Status
from calendoola_app.lib.database import Database
from calendoola_app.lib.loger import logger
from calendoola_app.lib.models.plan import Plan
from calendoola_app.lib.models.task import Task
from calendoola_app.lib.models.user import User


def operation_user_add(db, nickname, force):
    try:
        db.add_user(User(nickname=nickname))
        if force:
            db.set_current_user(nickname)
    except ce.UserAlreadyExist:
        print('User with nickname "{}" already exist'.format(nickname))
        logger().error('Tried to add existing user with nickname "{}"'.format(nickname))
    except ce.UserNotAuthorized:
        print('Use login to sign in or add new user')
        logger().error('Tried to work without authorization')
    else:
        logger().debug('Created user "{}"'.format(nickname))
        if force:
            logger().debug('Current user switched to "{}"'.format(nickname))


def operation_user_login(db, nickname):
    try:
        db.set_current_user(nickname)
    except ce.UserNotFound:
        print('User with nickname "{}" not exist'.format(nickname))
        logger().error('User with nickname "{}" not found'.format(nickname))
    else:
        logger().debug('Current user switched to "{}"'.format(nickname))


def operation_user_logout(db):
    db.remove_current_user()
    logger().debug('Deleted current user')


def operation_user_remove(db, nickname):
    try:
        db.remove_user(nickname)
    except ce.UserNotFound:
        print('User with nickname "{}" not exist'.format(nickname))
        logger().error('User with nickname "{}" not found'.format(nickname))
    except ce.UserNotAuthorized:
        print('Use login to sign in or add new user')
        logger().error('Tried to work without authorization')
    else:
        logger().debug('Current user switched to "{}"'.format(nickname))


def operation_user_info(db):
    try:
        user = db.get_current_user()
    except ce.UserNotAuthorized:
        print('You did not sign in')
        logger().error('Tried to print not logged in user')
    else:
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
        logger().debug('Printed information about current user')


def operation_task_add(db, description, priority, deadline, tags, parent_task_id):
    try:
        db.add_task(Task(info=description, priority=priority if priority else 1,
                         deadline=dp.get_deadline(deadline) if deadline else None,
                         tags=re.split("[^\w]", tags) if tags else [],
                         parent_id=parent_task_id))
    except ce.TaskNotFound:
        print('task with id {} does not exist'.format(parent_task_id))
        logger().error('Tried to add task as subtask to not existing task with id "{}"'.format(parent_task_id))
    except ValueError:
        print('Incorrect input date')
        logger().error('Entered incorrect deadline')
    except ce.UserNotAuthorized:
        print('Use login to sign in or add new user')
        logger().error('Tried to work without authorization')
    else:
        logger().debug('Created new task')


def operation_task_remove(db, id):
    try:
        db.remove_task(id)
    except ce.TaskNotFound:
        print('task with id {} does not exist'.format(id))
        logger().error('Tried to remove not existing task with id "{}"'.format(id))
    except ce.UserNotAuthorized:
        print('Use login to sign in or add new user')
        logger().error('Tried to work without authorization')
    else:
        logger().debug('Deleted task with id "{}"'.format(id))


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
    try:
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
        elif choice == 'archive':
            task_print(db.get_tasks(archive=True), colored)
        elif all:
            task_print(db.get_tasks(), colored, False)
        elif not choice:
            task_print(db.get_tasks(), colored)
    except ce.TaskNotFound:
        print('Task with id {} does not exist'.format(selected))
        logger().error('Tried to print not existing task with id "{}"'.format(selected))
    except ce.UserNotAuthorized:
        print('Use login to sign in or add new user')
        logger().error('Tried to work without authorization')
    else:
        if choice == 'id':
            logger().debug('Printed task with id "{}"'.format(selected))
        elif choice == 'tags':
            logger().debug('Printed tasks with tags "{}"'.format(re.sub('[^\w]', ', ', selected)))
        else:
            logger().debug('Printed all tasks')


def operation_task_finish(db, id):
    try:
        task_finish = db.get_tasks(id)
    except ce.TaskNotFound:
        print('task with id {} does not exist'.format(id))
        logger().error('Tried to finish not existing task with id "{}"'.format(id))
    else:
        if hasattr(task_finish, 'owner'):
            user_owner = db.get_users(task_finish.owner['nickname'])
            Database.get_task_by_id(user_owner.tasks, task_finish.owner['id'].split(const.ID_DELIMITER)).finish()
            user_owner.archive_task(task_finish.owner['id'])
        db.change_task(id, status=Status.FINISHED)
        if task_finish.plan is None:
            db.get_current_user().archive_task(id)
        db.serialize()
        logger().debug('Finished task with id "{}"'.format(id))


def operation_task_move(db, id_from, id_to):
    try:
        task_from = db.get_tasks(id_from)
    except ce.TaskNotFound:
        print('task with id {} does not exist'.format(id_from))
        logger().error('Tried to get not existing task with id "{}"'.format(id_from))
    else:
        try:
            task_to = db.get_tasks(id_to)
        except ce.TaskNotFound:
            if id_to == '0':
                task_from.parent_id = None
                db.add_task(copy.deepcopy(task_from))
                db.remove_task(task_from.id)
                logger().debug('Task with id "{}" became primary'.format(id_from))
            else:
                print('task with id {} does not exist'.format(id_to))
                logger().error('Tried to move not existing task with id "{}"'.format(id_to))
        else:
            task_to.append_task(copy.deepcopy(task_from))
            db.remove_task(id_from)
            logger().debug('Task with id "{}" became subtask "{}"'.format(id_to, id_from))


def operation_task_change(db, id, info, deadline, priority, status, append_tags, remove_tags):
    try:
        if status == Status.FINISHED:
            print('You can not finish task using changing. Use "task finish"')
            logger().warning('Tried to finish task from changing function')
            return
        db.change_task(id, info=info, deadline=deadline, priority=priority, status=status, plus_tag=append_tags,
                       minus_tag=remove_tags)
    except ce.TaskNotFound:
        print('Task with id "{}" does not exist'.format(id))
        logger().error('Tried to access to not existing task with id "{}"'.format(id))
    except ValueError:
        print('Incorrect input date')
        logger().error('Entered incorrect deadline')
    else:
        logger().debug('Changed information about task with id "{}"'.format(id))


def operation_task_share(db, id_from, nickname_to, delete, track):
    try:
        task_from = db.get_tasks(id_from)
    except ce.TaskNotFound:
        print('User with id "{}" does not exist'.format(id_from))
        logger().error('Tried to access to not existing tas kwith id "{}"'.format(id_from))
    else:
        try:
            user_to = db.get_users(nickname_to)
        except ce.UserNotFound:
            print('User with nickname "{}" does not exist'.format(nickname_to))
            logger().error('Tried to access to not existing user with nickname'.format(nickname_to))
        else:
            task_send = copy.deepcopy(task_from)
            task_send.id = Database.get_id(user_to.tasks)
            task_send.reset_sub_id()
            if track:
                if not hasattr(task_send.owner, 'owner'):
                    task_send.owner = {'nickname': db.get_current_user().nickname, 'id': id_from}
                else:
                    print('This task cant be tracked')
                    logger().warning('Tried to track task which already has owner')
            user_to.tasks.append(task_send)
            db.serialize()
            if delete:
                db.remove_task(id_from)
            logger().debug('Shared task with id "{}" to user with nickname "{}"'.format(id_from, nickname_to))


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
    try:
        period_options = dp.parse_period(period)
        db.add_plan(Plan(info=description, period=period_options['period'],
                         period_type=period_options['type'],
                         time_at=dp.parse_time(time) if time else None))
    except ValueError:
        print('Incorrect input date')
        logger().error('Entered incorrect weekday')
    else:
        logger().debug('Created plan')


def operation_plan_show(db, id, colored):
    try:
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
    except ce.PlanNotFound:
        logger().error('Tried to print not existing plan with id "{}"'.format(id))
    else:
        logger().debug('Printed plan with id "{}"'.format(id))


def operation_plan_remove(db, id):
    try:
        db.remove_plan(id)
    except ce.PlanNotFound:
        print('Plan with id "{}" does nit exist'.format(id))
        logger().error('Tried to remove not existing plan with id "{{"'.format(id))
    else:
        logger().debug('Removed plan with id "{}"'.format(id))


def check_plans(db):
    while True:
        for plan in db.get_plans():
            plan.check(db)
        for task in db.get_tasks():
            task.check(db)
        time.sleep(5)


def operation_task_restore(db, id):
    restore_task = copy.deepcopy(db.get_tasks(id, True))
    restore_task.id = Database.get_id(db.get_tasks())
    restore_task.reset_sub_id()
    restore_task.unfinish()
    db.add_task(restore_task)
    db.remove_task(id, True)
