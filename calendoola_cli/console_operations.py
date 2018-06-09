import calendar
import re
import sys

import date_parse as dp
import django.core.exceptions as django_ex
import django.db.utils
import printer
from calelib import CycleError
from calelib import Status


def operation_user_add(db, nickname, force):
    try:
        db.create_user(nickname)
        if force:
            operation_user_login(nickname, db)
    except django.db.utils.IntegrityError:
        print('User with nickname "{}" already exist'.format(nickname), file=sys.stderr)
        return 1


def operation_user_login(nickname, db):
    try:
        db.get_users(nickname)
        db.cfg.set_current_user(nickname)
    except django_ex.ObjectDoesNotExist:
        print('User with nickname "{}" not exist'.format(nickname), file=sys.stderr)
        return 1


def operation_user_logout(db):
    del db.current_user
    db.cfg.set_current_user('')


def operation_user_remove(db, nickname):
    try:
        db.remove_user(nickname)
    except django_ex.ObjectDoesNotExist:
        print('User with nickname "{}" not exist'.format(nickname), file=sys.stderr)
        return 1


def operation_user_info(db):
    try:
        user = db.get_users(db.cfg.get_config_field('current_user'))
        printer.print_user(user)
    except AttributeError:
        print('You did not sign in. Please login', file=sys.stderr)
        return 1


def operation_task_add(db, info, priority, deadline, tags, parent_task_id):
    try:
        deadline = dp.get_deadline(deadline) if deadline else None
        priority = priority if priority else 1
        tags = tags.strip().split() if tags else []

        db.create_task(info, priority, deadline, tags, parent_task_id)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(parent_task_id), file=sys.stderr)
        return 1
    except ValueError:
        print('Incorrect input date', file=sys.stderr)
        return 1


def operation_task_remove(db, task_id):
    try:
        db.remove_task(task_id)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(task_id), file=sys.stderr)
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
        print('Task with id {} does not exist'.format(selected), file=sys.stderr)
        return 1


def operation_task_finish(db, task_id):
    try:
        task_to_finish = db.get_tasks(task_id)

        if task_to_finish.plan is None:
            task_to_finish.finish()
            task_to_finish.pass_to_archive()
        else:
            print('You cannot archive planned task', file=sys.stderr)
    except django_ex.ObjectDoesNotExist:
        print('task with id {} does not exist'.format(task_id), file=sys.stderr)
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
        print('task with id {} does not exist'.format(bad_id), file=sys.stderr)
        return 1
    except CycleError:
        print('Task with id {} is parent of task with id {}'.format(id_from, id_to), file=sys.stderr)
        return 1


def operation_task_change(db, task_id, info, deadline, priority, status, append_tags, remove_tags):
    try:
        if status == Status.FINISHED:
            print('You can not finish task using changing. Use "task finish"')
        elif status == Status.UNFINISHED:
            print('You can not finish task using changing. Use "task restore"')
            return
        deadline = dp.get_deadline(deadline) if deadline else None
        append_tags = append_tags.strip().split() if append_tags else None
        remove_tags = remove_tags.strip().split() if remove_tags else None
        db.change_task(task_id, info=info, deadline=deadline, priority=priority, status=status,
                       plus_tags=append_tags,
                       minus_tags=remove_tags)
    except django_ex.ObjectDoesNotExist:
        print('Task with id "{}" does not exist'.format(task_id), file=sys.stderr)
        return 1
    except ValueError:
        print('Incorrect input date', file=sys.stderr)
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
            print('Task with id "{}" does not exist'.format(id_from), file=sys.stderr)
        else:
            print('User with nickname "{}" does not exist'.format(nickname_to), file=sys.stderr)
        return 1


def operation_task_unshare(db, task_id):
    """
    Unshare task from all users
    :param task_id: id of task to unshare
    :param db: param for serialization
    """
    try:
        task_to_unshare = db.get_tasks(task_id)
        performer_list = [db.get_users(performer) for performer in task_to_unshare.performers]
        if db.current_user.nickname not in task_to_unshare.performers:
            for performer in performer_list:
                performer.tasks.remove(task_to_unshare)
                task_to_unshare.remove_performer(performer.nickname)
        else:
            print('You have no permissions to unshare this task', file=sys.stderr)
    except django_ex.ObjectDoesNotExist:
        print('Task with id {} not found'.format(task_id), file=sys.stderr)
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
        print('Incorrect input', file=sys.stderr)
        return 1


def operation_plan_add(db, info, period_type, period_value, time):
    try:
        period_type, period_value = dp.parse_period(period_type, period_value)
        time_at = dp.parse_time(time) if time else None
        db.create_plan(info, period_value, period_type, time_at)
    except ValueError:
        print('Incorrect input date', file=sys.stderr)
        return 1


def operation_plan_change(db, plan_id, info, period_type, period_value, time_at):
    try:
        if not period_value and period_type:
            raise AttributeError
        period_type, period_value = dp.parse_period(period_type, period_value)
        time_at = dp.parse_time(time_at) if time_at else None
        db.change_plan(plan_id, info, period_type, period_value, time_at)
    except ValueError:
        print('Incorrect input date', file=sys.stderr)
        return 1
    except AttributeError:
        print('If you change period data, you should enter both parameters "-pt" and "-pv"', file=sys.stderr)
        return 1


def operation_plan_show(db, plan_id, colored):
    try:
        if plan_id:
            plan = db.get_plans(plan_id)
            printer.print_plan(plan)
        else:
            printer.print_plans(db.get_plans(), colored)
    except django_ex.ObjectDoesNotExist:
        print('Plan with id "{}" does nit exist'.format(plan_id), file=sys.stderr)
        return 1


def operation_plan_remove(db, plan_id):
    try:
        db.remove_plan(plan_id)
    except django_ex.ObjectDoesNotExist:
        print('Plan with id "{}" does nit exist'.format(plan_id), file=sys.stderr)
        return 1


def check_instances(db):
    for plan in db.get_plans():
        planned_task = plan.check_for_create()
        if planned_task:
            db.create_task(planned_task)
    for task in db.get_tasks():
        overdue_task = task.check_deadline()
        if overdue_task:
            choice = input('You overdue task "{}"\n Enter "d" to delete this task or "a" to archive:\n'
                           .format(overdue_task.info))
            if choice == 'a':
                operation_task_finish(db, overdue_task.id)
            else:
                operation_task_remove(db, overdue_task.id)
    for reminder in db.get_reminders():
        reminder.check_tasks()


def operation_task_restore(db, task_id):
    try:
        db.get_tasks(task_id).restore_from_archive()
    except django_ex.ObjectDoesNotExist:
        print('Task with id "{}" does not exists'.format(task_id), file=sys.stderr)
        return 1


def operation_reminder_add(db, remind_type, remind_before):
    remind_type = dp.parse_remind_type(remind_type)
    db.create_reminder(remind_type, remind_before)


def operation_reminder_remove(db, reminder_id):
    try:
        db.remove_reminder(reminder_id)
    except django_ex.ObjectDoesNotExist:
        print('Reminder with id "{}" does not exist'.format(reminder_id), file=sys.stderr)
    return 1


def operation_reminder_apply_task(db, reminder_id, task_id):
    bad_type = 'reminder'
    try:
        reminder = db.get_reminders(reminder_id)
        bad_type = 'task'
        task_to_append = db.get_tasks(task_id)
        reminder.apply_task(task_to_append)
    except django_ex.ObjectDoesNotExist:
        if bad_type == 'reminder':
            print('Reminder with id "{}" does not exist'.format(reminder_id), file=sys.stderr)
        else:
            print('Task with id "{}" does not exist'.format(task_id), file=sys.stderr)
        return 1


def operation_reminder_detach_task(db, reminder_id, task_id):
    bad_type = 'reminder'
    try:
        reminder = db.get_reminders(reminder_id)
        bad_type = 'task'
        task_to_append = db.get_tasks(task_id)
        reminder.detach_task(task_to_append)
    except django_ex.ObjectDoesNotExist:
        if bad_type == 'reminder':
            print('Reminder with id "{}" does not exist'.format(reminder_id), file=sys.stderr)
        else:
            print('Task with id "{}" does not exist'.format(task_id), file=sys.stderr)
        return 1


def operation_reminder_show(db, reminder_id):
    try:
        if reminder_id:
            printer.print_reminder(db.get_reminders(reminder_id))
        else:
            printer.print_reminders(db.get_reminders())

    except django_ex.ObjectDoesNotExist:
        print('Reminder with id "{}" does not exist'.format(reminder_id), file=sys.stderr)
    return 1


def operation_reminder_change(db, reminder_id, remind_type, remind_value):
    try:
        db.change_reminder(reminder_id, dp.parse_remind_type(remind_type), remind_value)
    except django_ex.ObjectDoesNotExist:
        print('Reminder with id "{}" does not exist'.format(reminder_id), file=sys.stderr)
    return 1
