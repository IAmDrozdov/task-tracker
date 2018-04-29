import copy
import re

from lib import calendar_custom as cc
from lib import datetime_parser as dp
from lib.database import Database
from lib.plan import Plan
from lib.task import Task
from lib.user import User


def operation_user_add(db, nickname, force):
    db.add_user(User(nickname))
    if force:
        db.set_current_user(nickname)


def operation_user_login(db, nickname):
    db.set_current_user(nickname)


def operation_user_logout(db):
    db.remove_current_user()


def operation_user_remove(db, nickname):
    db.remove_user(nickname)


def operation_user_info(db):
    db.get_current_user().print()


def operation_task_add(db, description, priority, deadline, tags, subtask):
    db.add_task(Task(info=description, priority=priority if priority else 1,
                     deadline=dp.get_deadline(deadline) if deadline else None,
                     tags=re.sub("[^\w]", " ", tags).split() if tags else [],
                     parent_id=subtask))


def operation_task_remove(db, id):
    db.remove_task(id)


def operation_task_show(db, id):
    pass


def operation_task_finish(db, id):
    db.change_task(id, status='finished')


def operation_task_move(db, id_from, id_to):
    task_from = db.get_tasks(id_from)
    send_task = copy.deepcopy(task_from)
    task_to = db.get_tasks(id_to)
    task_to.append_task(send_task)
    db.remove_task(id_from)


def operation_task_change(db, id, info, deadline, priority, status, append_tags, remove_tags):
    db.change_task(id, info=info, deadline=deadline, priority=priority, status=status, plus_tag=append_tags,
                   minus_tag=remove_tags)


def operation_task_share(db, id_from, nickname_to, delete):
    task_from = db.get_tasks(id_from)
    user_to = db.get_users(nickname_to)
    task_send = copy.deepcopy(task_from)
    task_send.id = Database.get_id(user_to.tasks)
    task_send.reset_sub_id()
    user_to.tasks.append(task_send)
    if delete:
        db.remove_task(id_from)


def operation_calendar_show(tasks, month, year):
    cc.print_month_calendar(tasks, month, year)


def operation_plan_add(db, description, period, time):
    period_options = dp.parse_period(period)
    db.add_plan(Plan(info=description, period=period_options[0],
                     period_type=period_options[1],
                     time_in=dp.parse_time(time) if time else None))


def operation_plan_show(db, id):
    pass


def operation_plan_remove(db, id):
    db.remove_plan(id)
