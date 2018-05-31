import calendar
import copy
import re
import time

import date_parse as dp
import django.core.exceptions as django_ex
import django.db.utils as django_db_ex
import printer
from calelib import Status
from calelib import (UserNotAuthorized,
                     UserNotFound,
                     TaskNotFound,
                     CycleError,
                     PlanNotFound,
                     DaemonAlreadyStarted,
                     DaemonIsNotStarted)
from calelib.models import Plan, Task, User


def operation_user_add(db, nickname, force, cfg):
    try:
        db.create_user(nickname)
        if force:
            operation_user_login(nickname, cfg)
    except django_db_ex.IntegrityError:
        print('User with nickname "{}" already exist'.format(nickname))


def operation_user_login(nickname, cfg):
    try:
        User.objects.get(nickname=nickname)
        cfg.set_current_user(nickname)
    except django_ex.ObjectDoesNotExist:
        print('User with nickname "{}" not exist'.format(nickname))


def operation_user_logout(cfg):
    cfg.set_current_user('')


def operation_user_remove(db, nickname):
    try:
        db.remove_user(nickname)
    except django_ex.ObjectDoesNotExist:
        print('User with nickname "{}" not exist'.format(nickname))


def operation_user_info(cfg):
    try:
        user = User.objects.get(nickname=cfg.get_config_field('current_user'))
    except django_ex.ObjectDoesNotExist:
        print('You did not sign in. Please login')
    else:
        printer.print_user(user)


def operation_task_add(db, description, priority, deadline, tags, parent_task_id):
    try:
        task = Task(info=description, priority=priority if priority else 1,
                    deadline=dp.get_deadline(deadline) if deadline else None,
                    tags=list(filter(None, re.split("[^\w]", tags.strip()))) if tags else [],
                    )
        if parent_task_id:
            parent_task = Task.objects.get(pk=parent_task_id)

            task.save()
            parent_task.add_subtask(task)
        else:
            task.save()
            db.create_task(task)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(parent_task_id))
    except ValueError:
        print('Incorrect input date')


def operation_task_remove(db, id):
    try:
        db.remove_task(id)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(id))


def operation_task_show(db, choice, selected, all, colored):
    try:
        if choice == 'id':
            task = db.get_tasks(selected)
            printer.print_main_task(task, colored)
        elif choice == 'tags':
            printer.print_task(db.get_tasks(), colored, tags=re.split('[^\w]', selected))
        elif choice == 'archive':
            printer.print_task(db.get_tasks(archive=True), colored)
        elif all:
            printer.print_task(db.get_tasks(), colored, short=False)
        elif not choice:
            printer.print_task(db.get_tasks(), colored)
    except TaskNotFound:
        print('Task with id {} does not exist'.format(selected))
    except UserNotAuthorized:
        print('Use login to sign in or add new user')


def operation_task_finish(db, id):
    try:
        prim_task_finish = db.get_tasks(id)
        if prim_task_finish.owner:
            owner = db.get_users(prim_task_finish.owner['nickname'])
            owner_task = owner.get_task(prim_task_finish.owner['id'])
            owner_task.finish()
            owner.archive_task(prim_task_finish.owner['id'])
        if prim_task_finish.user:
            user = db.get_users(prim_task_finish.user['nickname'])
            user_task = user.get_task(prim_task_finish.user['id'])
            user_task.finish()
            user.archive_task(prim_task_finish.user['id'])
        prim_task_finish.finish()
        if prim_task_finish.plan is None:
            db.get_current_user().archive_task(id)
        db.serialize()
    except UserNotAuthorized:
        print('Use login to sign in or add new user')
    except TaskNotFound:
        print('task with id {} does not exist'.format(id))


def operation_task_move(db, id_from, id_to):
    bad_id = None
    try:
        bad_id = id_from
        task_from = db.get_tasks(id_from)
        if id_to == '0':
            task_from.parent_id = None
            db.add_task(copy.deepcopy(task_from))
            db.remove_task(task_from.id)
        else:
            bad_id = id_to
            task_to = db.get_tasks(id_to)
            if not task_from.is_parent(id_to):
                copy_of_task_from = copy.deepcopy(task_from)
                task_to.append_task(copy_of_task_from)
                db.remove_task(id_from)
    except UserNotAuthorized:
        print('Use login to sign in or add new user')
    except TaskNotFound:
        print('task with id {} does not exist'.format(bad_id))
    except CycleError:
        print('Task with id {} is parent of task with id {}'.format(id_from, id_to))


def operation_task_change(db, id, info, deadline, priority, status, append_tags, remove_tags):
    try:
        if status == Status.FINISHED:
            print('You can not finish task using changing. Use "task finish"')
        elif status == Status.UNFINISHED:
            print('You can not finish task using changing. Use "task restore"')
            return
        db.change_task(id, info=info, deadline=dp.get_deadline(deadline), priority=priority, status=status,
                       plus_tag=append_tags,
                       minus_tag=remove_tags)
    except TaskNotFound:
        print('Task with id "{}" does not exist'.format(id))
    except ValueError:
        print('Incorrect input date')


def operation_task_share(db, id_from, nickname_to, delete, track):
    try:
        task_from = db.get_tasks(id_from)
        user_to = db.get_users(nickname_to)

        task_send = copy.deepcopy(task_from)
        task_send.id = Database.get_id(user_to.tasks)
        task_send.reset_sub_id()
        if track:
            if task_send.owner is None:
                task_send.add_owner(db.get_current_user().nickname, id_from)
                task_from.create_user(user_to.nickname, task_send.id)
            else:
                print('This task cant be tracked')
                return
        user_to.add_task(task_send)
        db.serialize()
        if delete:
            db.remove_task(id_from)
    except TaskNotFound:
        print('User with id "{}" does not exist'.format(id_from))

    except UserNotFound:
        print('User with nickname "{}" does not exist'.format(nickname_to))


def operation_task_unshare(db, id):
    """
    Unshare task from all users
    :param id: id of task to unshare
    :param db: param for serialization
    """
    try:
        task_to_unshare = db.get_tasks(id)
        user_with_task = db.get_users(task_to_unshare.user['nickname'])
        for task in user_with_task.get_all_tasks():
            if task.id == task_to_unshare.user['id']:
                user_with_task.remove_task(task.id)
                task_to_unshare.remove_user()
            db.serialize()
            break
    except TaskNotFound:
        print('Task with id {} not found'.format(id))


def operation_calendar_show(tasks, month, year):
    """
    Print Calendar of inputed date
    :param tasks: tasks what deadlines can be in entered month
    :param month: month to show
    :param year: year to show
    """
    try:
        printer.print_calendar(tasks, month, year)
    except calendar.IllegalMonthError:
        print('Incorrect input')


def operation_plan_add(db, description, period_type, period_value, time):
    try:
        p_type, p_val = dp.parse_period(period_type, period_value)
        db.create_plan(Plan(info=description, period=p_val, period_type=p_type,
                            time_at=dp.parse_time(time) if time else None))
    except ValueError:
        print('Incorrect input date')


def operation_plan_show(db, id, colored):
    try:
        if id:
            plan = db.get_plans(id)
            printer.print_plan(plan)
        else:
            printer.print_plans(db.get_plans(), colored)
    except django_ex.ObjectDoesNotExist:
        print('Plan with id "{}" does nit exist'.format(id))


def operation_plan_remove(db, id):
    try:
        db.remove_plan(id)
    except django_ex.ObjectDoesNotExist:
        print('Plan with id "{}" does nit exist'.format(id))


def _check_plans_and_tasks(db, daemon=True):
    def check_all(db):
        for plan in db.get_plans():
            plan.check(db)
        for task in db.get_tasks():
            task.check(db)

    while daemon:
        check_all(db)
        time.sleep(5)
    check_all(db)


def operation_task_restore(db, id):
    try:
        archived_task = copy.deepcopy(db.get_tasks(id, archive=True))
        if archived_task.parent_id is not None:

            parent_of_archived_task = db.get_tasks(archived_task.parent_id)
            archived_task.unfinish()
            archived_task.id = Database.get_id(parent_of_archived_task.subtasks)
            archived_task.reset_sub_id()
            parent_of_archived_task.append_task(archived_task)
            db.serialize()
        else:
            archived_task.id = Database.get_id(db.get_tasks())
            archived_task.reset_sub_id()
            db.add_task(archived_task)

        db.remove_task(id, archive=True)
    except TaskNotFound:
        print('Task with id "{}" does not exists'.format(id))


def run_daemon(db):
    try:
        self.daemon.run(self.check_plans_and_tasks, db)
    except DaemonAlreadyStarted:
        print('Daemon already started')


def stop_daemon():
    try:
        self.daemon.stop()
    except DaemonIsNotStarted:
        print('Daemon is not started')


def restart_daemon(db):
    daemon.restart(_check_plans_and_tasks, db)
