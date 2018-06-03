import calendar
import re
import time

import date_parse as dp
import django.core.exceptions as django_ex
import django.db.utils as django_db_ex
import printer
from calelib import (CycleError,
                     DaemonAlreadyStarted,
                     DaemonIsNotStarted
                     )
from calelib import Daemon
from calelib import Status
from calelib.models import Plan, Task, User


def operation_user_add(db, nickname, force, cfg):
    try:
        db.create_user(nickname)
        if force:
            operation_user_login(nickname, cfg)
    except django_db_ex.IntegrityError:
        print('User with nickname "{}" already exist'.format(nickname))
        return 1


def operation_user_login(nickname, cfg):
    try:
        User.objects.get(nickname=nickname)
        cfg.set_current_user(nickname)
    except django_ex.ObjectDoesNotExist:
        print('User with nickname "{}" not exist'.format(nickname))
        return 1


def operation_user_logout(cfg):
    cfg.set_current_user('')


def operation_user_remove(db, nickname):
    try:
        db.remove_user(nickname)
    except django_ex.ObjectDoesNotExist:
        print('User with nickname "{}" not exist'.format(nickname))
        return 1


def operation_user_info(cfg):
    try:
        user = User.objects.get(nickname=cfg.get_config_field('current_user'))
        printer.print_user(user)
    except django_ex.ObjectDoesNotExist:
        print('You did not sign in. Please login')
        return 1


def operation_task_add(db, info, priority, deadline, tags, parent_task_id):
    try:
        task = Task(info=info, priority=priority if priority else 1,
                    deadline=dp.get_deadline(deadline) if deadline else None,
                    tags=tags.strip().split() if tags else [],
                    )
        if parent_task_id:
            parent_task = db.get_tasks(parent_task_id)

            task.save()
            parent_task.add_subtask(task)
        else:
            task.save()
            db.create_task(task)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(parent_task_id))
        return 1
    except ValueError:
        print('Incorrect input date')
        return 1


def operation_task_remove(db, id):
    try:
        db.remove_task(id)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(id))
        return 1


def operation_task_show(db, choice, selected, colored):
    try:
        if choice == 'id':
            task = db.get_tasks(selected)
            printer.print_main_task(task)
        elif choice == 'tags':
            printer.print_task(db.get_tasks(), colored, tags=re.split('[^\w]', selected))
        elif choice == 'archive':
            printer.print_task(db.get_tasks(archive=True), colored)
        elif not choice:
            printer.print_task(db.get_tasks(), colored)
    except django_ex.ObjectDoesNotExist:
        print('Task with id {} does not exist'.format(selected))
        return 1
    except UserNotAuthorized:
        print('Use login to sign in or add new user')
        return 1


def operation_task_finish(db, id):
    try:
        task_to_finish = db.get_tasks(id)

        if task_to_finish.plan is None:
            task_to_finish.finish()
            task_to_finish.pass_to_archive()
        else:
            print('You cannot archive planned task')
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(id))
        return 1


def operation_task_move(db, id_from, id_to):
    bad_id = None
    try:
        bad_id = id_from
        task_from = db.get_tasks(id_from)
        if id_to == '0':
            db.create_task(task_from.get_copy())
            db.remove_task(task_from.id)
        else:
            bad_id = id_to
            task_to = db.get_tasks(id_to)
            task_to.add_subtask(task_from.get_copy())
            db.remove_task(id_from)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(bad_id))
        return 1
    except CycleError:
        print('Task with id {} is parent of task with id {}'.format(id_from, id_to))
        return 1


def operation_task_change(db, id, info, deadline, priority, status, append_tags, remove_tags):
    try:
        if status == Status.FINISHED:
            print('You can not finish task using changing. Use "task finish"')
        elif status == Status.UNFINISHED:
            print('You can not finish task using changing. Use "task restore"')
            return
        deadline = dp.get_deadline(deadline) if deadline else None
        append_tags = append_tags.strip().split() if append_tags else None
        remove_tags = remove_tags.strip().split() if remove_tags else None
        db.change_task(id, info=info, deadline=deadline, priority=priority, status=status,
                       plus_tags=append_tags,
                       minus_tags=remove_tags)
    except django_ex.ObjectDoesNotExist:
        print('Task with id "{}" does not exist'.format(id))
        return 1
    except ValueError:
        print('Incorrect input date')
        return 1


def operation_task_share(db, id_from, nickname_to):
    bad_type = 'task'
    try:
        task_from = db.get_tasks(id_from)
        bad_type = 'user'
        user_to = db.get_users(nickname_to)
        task_from.add_performer(nickname_to)
        user_to.add_task(task_from)
    except django_ex.ObjectDoesNotExist:
        if bad_type == 'task':
            print('Task with id "{}" does not exist'.format(id_from))
        else:
            print('User with nickname "{}" does not exist'.format(nickname_to))
        return 1


def operation_task_unshare(db, id):
    """
    Unshare task from all users
    :param id: id of task to unshare
    :param db: param for serialization
    """
    try:
        task_to_unshare = db.get_tasks(id)
        performer_list = [db.get_users(performer) for performer in task_to_unshare.performers]
        if db.current_user.nickname not in task_to_unshare.performers:
            for performer in performer_list:
                performer.tasks.remove(task_to_unshare)
                task_to_unshare.remove_performer(performer.nickname)
        else:
            print('You have no permissions to unshare this task')
    except django_ex.ObjectDoesNotExist:
        print('Task with id {} not found'.format(id))
        return 1


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
        return 1


def operation_plan_add(db, info, period_type, period_value, time):
    try:
        period_type, period_value = dp.parse_period(period_type, period_value)
        time_at = dp.parse_time(time) if time else None
        plan = Plan(info=info, period=period_value, period_type=period_type,
                    time_at=time_at)
        plan.save()
        db.create_plan(plan)
    except ValueError:
        print('Incorrect input date')
        return 1


def operation_plan_change(db, plan_id, info, period_type, period_value, time_at):
    try:
        if not period_value and period_type:
            raise AttributeError
        period_type, period_value = dp.parse_period(period_type, period_value)
        time_at = dp.parse_time(time_at) if time_at else None
        db.change_plan(plan_id, info, period_type, period_value, time_at)
    except ValueError:
        print('Incorrect input date')
        return 1
    except AttributeError:
        print('If you change period data, you should enter both parameters "-pt" and "-pv"')
        return 1


def operation_plan_show(db, id, colored):
    try:
        if id:
            plan = db.get_plans(id)
            printer.print_plan(plan)
        else:
            printer.print_plans(db.get_plans(), colored)
    except django_ex.ObjectDoesNotExist:
        print('Plan with id "{}" does nit exist'.format(id))
        return 1


def operation_plan_remove(db, id):
    try:
        db.remove_plan(id)
    except django_ex.ObjectDoesNotExist:
        print('Plan with id "{}" does nit exist'.format(id))
        return 1


def _check_plans_and_tasks(db, daemon=True):
    def check_all():
        for plan in db.get_plans():
            plan.check_for_create()
        for task in db.get_tasks():
            task.check_deadline()

    while daemon:
        check_all()
        time.sleep(5)
    check_all()


def operation_task_restore(db, task_id):
    try:
        db.get_tasks(task_id).restore_from_archive()
    except django_ex.ObjectDoesNotExisttFound:
        print('Task with id "{}" does not exists'.format(id))
        return 1


def run_daemon(db, pid_path):
    try:
        Daemon.run(_check_plans_and_tasks, db, pid_path)
    except (DaemonAlreadyStarted, FileNotFoundError):
        print('Daemon already started')
        return 1


def stop_daemon(pid_path):
    try:
        Daemon.stop(pid_path)
    except DaemonIsNotStarted:
        print('Daemon is not started')
        return 1


def restart_daemon(db, pid_path):
    Daemon.restart(_check_plans_and_tasks, db, pid_path)
