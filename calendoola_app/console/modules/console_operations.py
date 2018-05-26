import calendar
import copy
import re
import time

import calendoola_app.calendoola_lib.etc.custom_exceptions as ce
from calendoola_app.calendoola_lib.etc import datetime_parser as dp
from calendoola_app.calendoola_lib.modules.constants import Status
from calendoola_app.calendoola_lib.etc.daemon import Daemon
from calendoola_app.calendoola_lib.db.database import Database
from calendoola_app.calendoola_lib.modules.loger import logger
from calendoola_app.calendoola_lib.models.plan import Plan
from calendoola_app.calendoola_lib.models.task import Task
from calendoola_app.calendoola_lib.models.user import User
from calendoola_app.console.modules import printer


class ConsoleOperations:
    def __init__(self, logger_path, pid_path, log_level):
        self.logger = logger(logger_path, log_level)
        self.daemon = Daemon(pid_path)

    def operation_user_add(self, db, nickname, force):

        try:
            db.add_user(User(nickname=nickname))
            if force:
                db.set_current_user(nickname)
        except ce.UserAlreadyExists:
            print('User with nickname "{}" already exist'.format(nickname))
            self.logger.error('Tried to add existing user with nickname "{}"'.format(nickname))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            self.logger.error('Tried to work without authorization')
        else:
            self.logger.debug('Created user "{}"'.format(nickname))
            if force:
                self.logger.debug('Current user switched to "{}"'.format(nickname))

    def operation_user_login(self, db, nickname):

        try:
            db.set_current_user(nickname)
        except ce.UserNotFound:
            print('User with nickname "{}" not exist'.format(nickname))
            self.logger.error('User with nickname "{}" not found'.format(nickname))
        else:
            self.logger.debug('Current user switched to "{}"'.format(nickname))

    def operation_user_logout(self, db):
        db.remove_current_user()
        self.logger.debug('Deleted current user')

    def operation_user_remove(self, db, nickname):

        try:
            db.remove_user(nickname)
        except ce.UserNotFound:
            print('User with nickname "{}" not exist'.format(nickname))
            self.logger.error('User with nickname "{}" not found'.format(nickname))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            self.logger.error('Tried to work without authorization')
        else:
            self.logger.debug('Current user switched to "{}"'.format(nickname))

    def operation_user_info(self, db):
        try:
            user = db.get_current_user()
        except ce.UserNotAuthorized:
            print('You did not sign in')
            self.logger.error('Tried to print not logged in user')
        else:
            printer.print_user(user)
            self.logger.debug('Printed information about current user')

    def operation_task_add(self, db, description, priority, deadline, tags, parent_task_id):

        try:
            db.add_task(Task(info=description, priority=priority if priority else 1,
                             deadline=dp.get_deadline(deadline) if deadline else None,
                             tags=list(filter(None, re.split("[^\w]", tags.strip()))) if tags else [],
                             parent_id=parent_task_id))
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(parent_task_id))
            self.logger.error(
                'Tried to add task as subtask to not existing task with id "{}"'.format(parent_task_id))
        except ValueError:
            print('Incorrect input date')
            self.logger.error('Entered incorrect deadline')
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            self.logger.error('Tried to work without authorization')
        else:
            self.logger.debug('Created new task')

    def operation_task_remove(self, db, id):

        try:
            db.remove_task(id)
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(id))
            self.logger.error('Tried to remove not existing task with id "{}"'.format(id))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            self.logger.error('Tried to work without authorization')
        else:
            self.logger.debug('Deleted task with id "{}"'.format(id))

    def operation_task_show(self, db, choice, selected, all, colored):

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
        except ce.TaskNotFound:
            print('Task with id {} does not exist'.format(selected))
            self.logger.error('Tried to print not existing task with id "{}"'.format(selected))
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            self.logger.error('Tried to work without authorization')
        else:
            if choice == 'id':
                self.logger.debug('Printed task with id "{}"'.format(selected))
            elif choice == 'tags':
                self.logger.debug('Printed tasks with tags "{}"'.format(re.sub('[^\w]', ', ', selected)))
            else:
                self.logger.debug('Printed all tasks')

    def operation_task_finish(self, db, id):

        try:
            prim_task_finish = db.get_tasks(id)
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            self.logger.error('Tried to work without authorization')
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(id))
            self.logger.error('Tried to finish not existing task with id "{}"'.format(id))
        else:
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
            self.logger.debug('Finished task with id "{}"'.format(id))

    def operation_task_move(self, db, id_from, id_to):

        try:
            task_from = db.get_tasks(id_from)
        except ce.UserNotAuthorized:
            print('Use login to sign in or add new user')
            self.logger.error('Tried to work without authorization')
        except ce.TaskNotFound:
            print('task with id {} does not exist'.format(id_from))
            self.logger.error('Tried to get not existing task with id "{}"'.format(id_from))
        else:
            try:
                task_to = db.get_tasks(id_to)
            except ce.TaskNotFound:
                if id_to == '0':
                    task_from.parent_id = None
                    db.add_task(copy.deepcopy(task_from))
                    db.remove_task(task_from.id)
                    self.logger.debug('Task with id "{}" became primary'.format(id_from))
                else:
                    print('task with id {} does not exist'.format(id_to))
                    self.logger.error('Tried to move not existing task with id "{}"'.format(id_to))
            else:
                if not task_from.is_parent(id_to):
                    copy_of_task_from = copy.deepcopy(task_from)
                    task_to.append_task(copy_of_task_from)
                    db.remove_task(id_from)
                    self.logger.debug('Task with id "{}" became subtask "{}"'.format(id_to, id_from))
                else:
                    print('Task with id {} is parent of task with id {}'.format(id_from, id_to))
                    self.logger.error('Tried to move parent task to self subtask')

    def operation_task_change(self, db, id, info, deadline, priority, status, append_tags, remove_tags):

        try:
            if status == Status.FINISHED:
                print('You can not finish task using changing. Use "task finish"')
                self.logger.warning('Tried to finish task from changing function')
            elif status == Status.UNFINISHED:
                print('You can not finish task using changing. Use "task restore"')
                self.logger.warning('Tried to unfinish task from changing function')
                return
            db.change_task(id, info=info, deadline=deadline, priority=priority, status=status, plus_tag=append_tags,
                           minus_tag=remove_tags)
        except ce.TaskNotFound:
            print('Task with id "{}" does not exist'.format(id))
            self.logger.error('Tried to access to not existing task with id "{}"'.format(id))
        except ValueError:
            print('Incorrect input date')
            self.logger.error('Entered incorrect deadline')
        else:
            self.logger.debug('Changed information about task with id "{}"'.format(id))

    def operation_task_share(self, db, id_from, nickname_to, delete, track):

        try:
            task_from = db.get_tasks(id_from)
        except ce.TaskNotFound:
            print('User with id "{}" does not exist'.format(id_from))
            self.logger.error('Tried to access to not existing tas kwith id "{}"'.format(id_from))
        else:
            try:
                user_to = db.get_users(nickname_to)
            except ce.UserNotFound:
                print('User with nickname "{}" does not exist'.format(nickname_to))
                self.logger.error('Tried to access to not existing user with nickname'.format(nickname_to))
            else:
                task_send = copy.deepcopy(task_from)
                task_send.id = Database.get_id(user_to.tasks)
                task_send.reset_sub_id()
                if track:
                    if task_send.owner is None:
                        task_send.add_owner(db.get_current_user().nickname, id_from)
                        task_from.add_user(user_to.nickname, task_send.id)
                    else:
                        print('This task cant be tracked')
                        self.logger.warning('Tried to track task which already tracking')
                user_to.add_task(task_send)
                db.serialize()
                if delete:
                    db.remove_task(id_from)

                self.logger.debug(
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
            for task in user_with_task.get_all_tasks():
                if task.id == task_to_unshare.user['id']:
                    user_with_task.remove_task(task.id)
                    task_to_unshare.remove_user()
                db.serialize()
                break
            self.logger.debug('Unshared task with id {}'.format(id))
        except ce.TaskNotFound:
            print('Task with id {} not found'.format(id))
            self.logger.error('Tried ti unshared not existing task with id  {}'.format(id))

    def operation_calendar_show(self, tasks, month, year):

        try:
            printer.print_calendar(tasks, month, year)
            self.logger.debug('Printed calendar for {}.{}'.format(month, year))
        except calendar.IllegalMonthError:
            print('Incorrect input')
            self.logger.error('Tried to output incorrect month')

    def operation_plan_add(self, db, description, period_type, period_value, time):

        try:
            db.add_plan(Plan(info=description, period=dp.parse_period(period_type, period_value),
                             time_at=dp.parse_time(time) if time else None))
        except ValueError:
            print('Incorrect input date')
            self.logger.error('Entered incorrect weekday')
        else:
            self.logger.debug('Created plan')

    def operation_plan_show(self, db, id, colored):

        try:
            if id:
                plan = db.get_plans(id)
                printer.print_plan(plan)
            else:
                printer.print_plans(db.get_plans(), colored)
        except ce.PlanNotFound:
            self.logger.error('Tried to print not existing plan with id "{}"'.format(id))
        else:
            self.logger.debug('Printed plan with id "{}"'.format(id))

    def operation_plan_remove(self, db, id):

        try:
            db.remove_plan(id)
        except ce.PlanNotFound:
            print('Plan with id "{}" does nit exist'.format(id))
            self.logger.error('Tried to remove not existing plan with id "{{"'.format(id))
        else:
            self.logger.debug('Removed plan with id "{}"'.format(id))

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
        except ce.TaskNotFound:
            print('Task with id "{}" does not exists'.format(id))
            self.logger.error('Tried ti restore not existing task with id "{}"'.format(id))
        else:
            self.logger.debug('Restored task with id "{}"'.format(id))

    def run_daemon(self, db):
        try:
            self.daemon.run(self.check_plans_and_tasks, db)
        except ce.DaemonAlreadyStarted:
            print('Daemon already started')
            self.logger.error('Tried to run already started deemon')
        else:
            self.logger.debug('')

    def stop_daemon(self):
        try:
            self.daemon.stop()
        except ce.DaemonIsNotStarted:
            print('Daemon is not started')
            self.logger.error("Tried to stop unstarted daemon")
        else:
            self.logger.debug('Stopped daemon')

    def restart_daemon(self, db):
        self.daemon.restart(self.check_plans_and_tasks, db)
