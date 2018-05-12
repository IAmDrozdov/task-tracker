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
from calendoola_app.lib.daemon import Daemon
from calendoola_app.lib.models.task import Task
from calendoola_app.lib.models.user import User


class ConsoleOperations:
    def __init__(self, logger_path, pid_path):
        self.log = logger_path
        self.daemon = Daemon(pid_path, logger_path)

    def operation_user_add(self, db, nickname, force):

        try:
            db.add_user(User(nickname=nickname))
            if force:
                db.set_current_user(nickname)
        except ce.UserAlreadyExists:
            print('User with nickname "{}" already exist'.format(nickname))
            logger(self.log).error('Tried to add existing user with nickname "{}"'.format(nickname))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            logger(self.log).error('Tried to work without authorization')
        else:
            logger(self.log).debug('Created user "{}"'.format(nickname))
            if force:
                logger(self.log).debug('Current user switched to "{}"'.format(nickname))

    def operation_user_login(self, db, nickname):

        try:
            db.set_current_user(nickname)
        except ce.UserNotFound:
            print('User with nickname "{}" not exist'.format(nickname))
            logger(self.log).error('User with nickname "{}" not found'.format(nickname))
        else:
            logger(self.log).debug('Current user switched to "{}"'.format(nickname))

    def operation_user_logout(self, db):

        db.remove_current_user()
        logger(self.log).debug('Deleted current user')

    def operation_user_remove(self, db, nickname):

        try:
            db.remove_user(nickname)
        except ce.UserNotFound:
            print('User with nickname "{}" not exist'.format(nickname))
            logger(self.log).error('User with nickname "{}" not found'.format(nickname))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            logger(self.log).error('Tried to work without authorization')
        else:
            logger(self.log).debug('Current user switched to "{}"'.format(nickname))

    def operation_user_info(self, db):

        try:
            user = db.get_current_user()
        except ce.UserNotAuthorized:
            print('You did not sign in')
            logger(self.log).error('Tried to print not logged in user')
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
            logger(self.log).debug('Printed information about current user')

    def operation_task_add(self, db, description, priority, deadline, tags, parent_task_id):

        try:
            db.add_task(Task(info=description, priority=priority if priority else 1,
                             deadline=dp.get_deadline(deadline) if deadline else None,
                             tags=re.split("[^\w]", tags) if tags else [],
                             parent_id=parent_task_id))
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(parent_task_id))
            logger(self.log).error(
                'Tried to add task as subtask to not existing task with id "{}"'.format(parent_task_id))
        except ValueError:
            print('Incorrect input date')
            logger(self.log).error('Entered incorrect deadline')
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            logger(self.log).error('Tried to work without authorization')
        else:
            logger(self.log).debug('Created new task')

    def operation_task_remove(self, db, id):

        try:
            db.remove_task(id)
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(id))
            logger(self.log).error('Tried to remove not existing task with id "{}"'.format(id))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            logger(self.log).error('Tried to work without authorization')
        else:
            logger(self.log).debug('Deleted task with id "{}"'.format(id))

    def task_print(self, tasks, colored, short=True, tags=None):

        if colored:
            priority_colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.LIGHTMAGENTA_EX, Fore.RED]
        else:
            priority_colors = [Fore.RESET] * 6
        for task in tasks:
            if tags:
                if all(elem in task.tags for elem in re.split("[^\w]", tags)):
                    subtasks_print = '' if len(task.subtasks) == 0 else '(' + str(len(task.subtasks)) + ')'
                    print(priority_colors[task.priority - 1] + 'ID: {} | {} {}'.format(task.id, task.info,
                                                                                       subtasks_print))
                self.task_print(task.subtasks, colored, tags=tags)
            elif short:
                subtasks_print = '' if len(task.subtasks) == 0 else '(' + str(len(task.subtasks)) + ')'
                print(priority_colors[task.priority - 1] + 'ID: {} | {} {}'.format(task.id, task.info, subtasks_print))
            elif not short:
                offset = '' if task.indent == 0 else task.indent * ' ' + task.indent * ' *'
                print(priority_colors[task.priority - 1] + offset + '| {} | {}'.format(task.id, task.info))
                self.task_print(task.subtasks, colored, False)

    def operation_task_show(self, db, choice, selected, all, colored):

        try:
            if choice == 'id':
                task = db.get_tasks(selected)
                deadline_print = dp.parse_iso_pretty(task.deadline) if task.deadline else 'No deadline'
                tags_print = ', '.join(task.tags) if len(task.tags) > 0 else 'No tags'
                print('Information: {}\nID: {}\nDeadline: {}\nStatus: {}\nCreated: {}\nLast change: {}\nTags: {}'
                      .format(task.info, task.id, deadline_print, task.status,
                              dp.parse_iso_pretty(task.date), dp.parse_iso_pretty(task.last_change), tags_print))
                print('Subtasks:')
                self.task_print(task.subtasks, colored)
            elif choice == 'tags':
                self.task_print(db.get_tasks(), colored, tags=selected)
            elif choice == 'archive':
                self.task_print(db.get_tasks(archive=True), colored)
            elif all:
                self.task_print(db.get_tasks(), colored, False)
            elif not choice:
                self.task_print(db.get_tasks(), colored)
        except ce.TaskNotFound:
            print('Task with id {} does not exist'.format(selected))
            logger(self.log).error('Tried to print not existing task with id "{}"'.format(selected))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            logger(self.log).error('Tried to work without authorization')
        else:
            if choice == 'id':
                logger(self.log).debug('Printed task with id "{}"'.format(selected))
            elif choice == 'tags':
                logger(self.log).debug('Printed tasks with tags "{}"'.format(re.sub('[^\w]', ', ', selected)))
            else:
                logger(self.log).debug('Printed all tasks')

    def operation_task_finish(self, db, id):

        try:
            task_finish = db.get_tasks(id)
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(id))
            logger(self.log).error('Tried to finish not existing task with id "{}"'.format(id))
        else:
            if hasattr(task_finish, 'owner'):
                user_owner = db.get_users(task_finish.owner['nickname'])
                Database.get_task_by_id(user_owner.tasks, task_finish.owner['id'].split(const.ID_DELIMITER)).finish()
                user_owner.archive_task(task_finish.owner['id'])
            task_finish.finish()
            if task_finish.plan is None:
                db.get_current_user().archive_task(id)
            db.serialize()
            logger(self.log).debug('Finished task with id "{}"'.format(id))

    def operation_task_move(self, db, id_from, id_to):

        try:
            task_from = db.get_tasks(id_from)
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(id_from))
            logger(self.log).error('Tried to get not existing task with id "{}"'.format(id_from))
        else:
            try:
                task_to = db.get_tasks(id_to)
            except ce.TaskNotFound:
                if id_to == '0':
                    task_from.parent_id = None
                    db.add_task(copy.deepcopy(task_from))
                    db.remove_task(task_from.id)
                    logger(self.log).debug('Task with id "{}" became primary'.format(id_from))
                else:
                    print('task with id {} does not exist'.format(id_to))
                    logger(self.log).error('Tried to move not existing task with id "{}"'.format(id_to))
            else:
                task_to.append_task(copy.deepcopy(task_from))
                db.remove_task(id_from)
                logger(self.log).debug('Task with id "{}" became subtask "{}"'.format(id_to, id_from))

    def operation_task_change(self, db, id, info, deadline, priority, status, append_tags, remove_tags):

        try:
            if status == Status.FINISHED:
                print('You can not finish task using changing. Use "task finish"')
                logger(self.log).warning('Tried to finish task from changing function')
                return
            db.change_task(id, info=info, deadline=deadline, priority=priority, status=status, plus_tag=append_tags,
                           minus_tag=remove_tags)
        except ce.TaskNotFound:
            print('Task with id "{}" does not exist'.format(id))
            logger(self.log).error('Tried to access to not existing task with id "{}"'.format(id))
        except ValueError:
            print('Incorrect input date')
            logger(self.log).error('Entered incorrect deadline')
        else:
            logger(self.log).debug('Changed information about task with id "{}"'.format(id))

    def operation_task_share(self, db, id_from, nickname_to, delete, track):

        try:
            task_from = db.get_tasks(id_from)
        except ce.TaskNotFound:
            print('User with id "{}" does not exist'.format(id_from))
            logger(self.log).error('Tried to access to not existing tas kwith id "{}"'.format(id_from))
        else:
            try:
                user_to = db.get_users(nickname_to)
            except ce.UserNotFound:
                print('User with nickname "{}" does not exist'.format(nickname_to))
                logger(self.log).error('Tried to access to not existing user with nickname'.format(nickname_to))
            else:
                task_send = copy.deepcopy(task_from)
                task_send.id = Database.get_id(user_to.tasks)
                task_send.reset_sub_id()
                if track:
                    if not hasattr(task_send, 'owner'):
                        task_send.owner = {'nickname': db.get_current_user().nickname, 'id': id_from}
                        task_from.user = {'nickname': user_to.nickname, 'id': task_send.id}
                    else:
                        print('This task cant be tracked')
                        logger(self.log).warning('Tried to track task which already tracking')
                user_to.tasks.append(task_send)
                db.serialize()
                if delete:
                    db.remove_task(id_from)
                logger(self.log).debug(
                    'Shared task with id "{}" to user with nickname "{}"'.format(id_from, nickname_to))

    def operation_task_unshare(self, db, id):
        """
        Unshare task from all users
        :param id: id of task to unshare
        :param db: param for serialization
        """
        try:
            task_to_unshare = db.get_tasks(id)
            user_with_task = db.get_users(task_to_unshare.user['nickname'])
            for task in user_with_task.tasks:
                if task.id == task_to_unshare.user['id']:
                    user_with_task.tasks.remove(task)
                    del task_to_unshare.user
                    db.serialize()
                    break
            logger(self.log).debug('Unshared task with id {}'.format(id))
            """
            переместить удаление задачи непосредтсвенно в класс юзера, и все входждения почистить, атк же пересмотреть
            ахивацию задач при проверке задач. 
            Доделать аншеер, постараться все функции, связанные с юзером задачей и плано пернести непосредственно в сами
            их классы.
            """
        except ce.TaskNotFound:
            print('Task with id {} not found'.format(id))
            logger(self.log).error('Tried ti unshared not existing task with id  {}'.format(id))

    def operation_calendar_show(self, tasks, month, year):

        cal = calendar.Calendar()
        try:
            for _ in cal.itermonthdays(year, month):
                pass
        except calendar.IllegalMonthError:
            print('Incorrect input')
            logger(self.log).error('Tried to output incorrect month')
        else:
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

            logger(self.log).debug('Printed calendar for {}.{}'.format(month, year))

    def operation_plan_add(self, db, description, period, time):

        try:
            period_options = dp.parse_period(period)
            db.add_plan(Plan(info=description, period=period_options['period'],
                             period_type=period_options['type'],
                             time_at=dp.parse_time(time) if time else None))
        except ValueError:
            print('Incorrect input date')
            logger(self.log).error('Entered incorrect weekday')
        else:
            logger(self.log).debug('Created plan')

    def operation_plan_show(self, db, id, colored):

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
                        next_print += dp.get_weekday_word(
                            min(filter(lambda x: x > datetime.now().weekday(), plan.period)))
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
            logger(self.log).error('Tried to print not existing plan with id "{}"'.format(id))
        else:
            logger(self.log).debug('Printed plan with id "{}"'.format(id))

    def operation_plan_remove(self, db, id):

        try:
            db.remove_plan(id)
        except ce.PlanNotFound:
            print('Plan with id "{}" does nit exist'.format(id))
            logger(self.log).error('Tried to remove not existing plan with id "{{"'.format(id))
        else:
            logger(self.log).debug('Removed plan with id "{}"'.format(id))

    @staticmethod
    def check_plans_and_tasks(db):

        while True:
            for plan in db.get_plans():
                plan.check(db)
            for task in db.get_tasks():
                task.check(db)
            time.sleep(5)

    def operation_task_restore(self, db, id):
        try:
            restore_task = copy.deepcopy(db.get_tasks(id, True))
            restore_task.id = Database.get_id(db.get_tasks())
            restore_task.reset_sub_id()
            restore_task.unfinish()
            db.add_task(restore_task)
            db.remove_task(id, True)
        except ce.TaskNotFound:
            print('Task with id "{}" does not exists'.format(id))
            logger(self.log).error('Tried ti restore not existing task with id "{}"'.format(id))
        else:
            logger(self.log).debug('Restored task with id "{}"'.format(id))

    def run_daemon(self, db):
        try:
            self.daemon.run(self.check_plans_and_tasks, db)
        except ce.DaemonAlreadyStarted:
            print('Daemon already started')
            logger(self.log).error('Tried to run already started deemon')
        else:
            logger(self.log).debug('')

    def stop_daemon(self):
        try:
            self.daemon.stop()
        except ce.DaemonIsNotStarted:
            print('Daemon is not started')
            logger(self.log).error("Tried to stop unstarted daemon")
        else:
            logger(self.log).debug('Stopped daemon')

    def restart_daemon(self, db):
        self.daemon.restart(self.check_plans_and_tasks, db)
