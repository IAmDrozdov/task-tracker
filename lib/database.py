import json
import re

import jsonpickle

from lib import custom_exceptions as ce
from lib import datetime_parser
from lib.constants import Constants as const


class Database:
    def __init__(self):
        """
        Class for working with database
        """
        try:
            with open(const.DATABASE_PATH, mode='r', encoding='utf-8') as db:
                json_file = db.read()
            full = jsonpickle.decode(json_file)
        except json.decoder.JSONDecodeError or FileNotFoundError:
            full = None

        self.users = full.users if full else []
        self.current_user = full.current_user if full else None
        self.path = const.DATABASE_PATH

    def serialize(self):
        """
        Serialize database in json file
        """
        temp_path = self.path
        del self.path
        with open(temp_path, mode='w+', encoding='utf-8') as db:
            to_write = jsonpickle.encode(self, make_refs=False)
            db.write(to_write)
        self.path = temp_path

    def check_user_exist(self, nickname):
        """
        Checking user for already existing in database
        :param nickname: nickname of user to check
        """
        for user in self.users:
            if user.nickname == nickname:
                raise ce.UserAlreadyExist

    def add_user(self, new_user):
        """
        Adding new user in database
        :param new_user: object of new user
        """
        self.check_user_exist(new_user.nickname)
        self.users.append(new_user)
        self.serialize()

    def set_current_user(self, new_current_user_nickname):
        """
        Change current user
        :param new_current_user_nickname: nickname of user which will me new current user
        """
        for user in self.users:
            if user.nickname == new_current_user_nickname:
                self.current_user = new_current_user_nickname
                self.serialize()
                break
        else:
            raise ce.UserNotFound

    def get_current_user(self):
        """
        Get current user object
        :return: current user object
        """
        return self.get_users(self.current_user)

    def remove_current_user(self):
        """
        Remove current user
        """
        self.current_user = None
        self.serialize()

    def remove_user(self, nickname):
        """
        Remove user from database
        :param nickname: nickname of user to remove
        """
        self.check_current()
        for user in self.users:
            if user.nickname == nickname:
                if self.current_user == nickname:
                    self.current_user = None
                self.users.remove(user)
                self.serialize()
                break
        else:
            raise ce.UserNotFound

    def get_users(self, nickname=None):
        """
        Depending on the param returns all users or only given nickname
        :param nickname: nickname of user to return
        :return: list of users or user
        """
        if nickname is None:
            return [user for user in self.users]
        else:
            for user in self.users:
                if user.nickname == nickname:
                    return user
            else:
                raise ce.UserNotFound

    @staticmethod
    def get_id(list_to, sub=False):
        """
        Generetion id for item in list. Taking last item in container and increment its id
        :param list_to: container where item will be appended
        :param sub: return value for primary task or not
        :return: integer number
        """
        if sub:
            if len(list_to) == 0:
                return '1'
            else:
                pre_id = list_to[-1].id.split(const.ID_DELIMITER)
                return str(int(pre_id[-1]) + 1)
        else:
            return str(int(list_to[-1].id) + 1) if len(list_to) != 0 else '1'

    def check_current(self):
        """
        Checking for authorization in database
        :return: returns object of current user
        """
        if self.current_user:
            for user in self.users:
                if user.nickname == self.current_user:
                    return user
        else:
            raise ce.UserNotAuthorized

    def add_plan(self, new_plan):
        """
        Append plan to current user plans
        :param new_plan:
        """
        current = self.check_current()
        new_plan.id = Database.get_id(current.plans)
        current.plans.append(new_plan)
        self.serialize()

    def remove_plan(self, id):
        """
        Removes plan from current user plans
        :param id: id of plan to remove
        """
        current = self.check_current()
        current.plans.remove(self.get_plans(id))
        for task in self.get_tasks():
            if task.plan == id:
                self.remove_task(task.id)
                break
        self.serialize()

    def get_plans(self, id=None):
        """
        Get plan object  via ID or all
        :param id: id of plan to return
        :return: list of plans or plan with this id
        """
        current = self.check_current()
        if id is None:
            return current.plans
        else:
            for plan in current.plans:
                if plan.id == id:
                    return plan
            else:
                raise ce.PlanNotFound

    @staticmethod
    def get_task_by_id(tasks, idx_mass, remove=False):
        """
        Recursively search task in list of tasks via id. Comparing each level of tasks with each number in massive of id
        :param tasks: list of tasks
        :param idx_mass: splitted id of task to search
        :param remove: if True delete founded task
        :return: object task with this id
        """
        for task in tasks:
            if int(task.id.split(const.ID_DELIMITER)[-1]) == int(idx_mass[0]):
                if len(idx_mass) > 1:
                    return Database.get_task_by_id(task.subtasks, idx_mass[1:], remove)
                else:
                    if remove:
                        tasks.remove(task)
                        return True
                    else:
                        return task

    def get_tasks(self, id=None, archive=False):
        """
        Get list of tasks or task by id or archve tasks
        :param id: id of task to return
        :param archive: if True returns archive tasks
        :return: list of tasks, archive tasks or task with this id
        """
        current = self.check_current()
        if id:
            found_task = Database.get_task_by_id(current.tasks, id.split(const.ID_DELIMITER))
            if found_task:
                return found_task
            else:
                raise ce.TaskNotFound
        elif archive:
            return current.archive
        else:
            return current.tasks

    def add_task(self, new_task):
        """
        Adding task to list of currrent user tasks
        :param new_task: object of new task
        """
        current = self.check_current()
        if new_task.parent_id:
            parent_task = Database.get_task_by_id(current.tasks, new_task.parent_id.split(const.ID_DELIMITER))
            if parent_task:
                new_task.id = parent_task.id + const.ID_DELIMITER + Database.get_id(parent_task.subtasks, True)
                new_task.indent = new_task.id.count(const.ID_DELIMITER)
                parent_task.subtasks.append(new_task)
            else:
                raise ce.TaskNotFound
        else:
            new_task.id = Database.get_id(current.tasks)
            current.tasks.append(new_task)
        self.serialize()

    def remove_task(self, id):
        """
        remove task from current user tasks
        :param id: id of task to delete
        """
        current = self.check_current()
        if not Database.get_task_by_id(current.tasks, id.split(const.ID_DELIMITER), True):
            raise ce.TaskNotFound
        self.serialize()

    def change_task(self, id, info=None, deadline=None, priority=None, status=None, plus_tag=None, minus_tag=None):
        """
        Change information about task
        :param id: change id
        :param info: change information
        :param deadline: change deadline
        :param priority: change priority
        :param status: change status
        :param plus_tag: add new tags
        :param minus_tag: remove tags
        """
        self.check_current()
        found_task = self.get_tasks(id)
        if info:
            found_task.info = info
        if deadline:
            found_task.deadline = datetime_parser.get_deadline(deadline)
        if priority:
            found_task.priority = priority
        if status == const.STATUS_FINISHED:
            found_task.finish()
        else:
            found_task.status = status
        if plus_tag:
            for tag in re.split("[^\w]", plus_tag):
                found_task.tags.append(tag)
            found_task.tags = list(set(found_task.tags))
        if minus_tag:
            for tag in re.split("[^\w]", minus_tag):
                found_task.tags.remove(tag)
        found_task.changed()
        self.serialize()
