import json
import re
import copy

import jsonpickle

from lib import custom_exceptions
from lib import datetime_parser
from lib.constants import Constants as const


class Database:
    def __init__(self, path):
        try:
            with open(path, mode='r', encoding='utf-8') as db:
                json_file = db.read()
            full = jsonpickle.decode(json_file)
        except json.decoder.JSONDecodeError or FileNotFoundError:
            full = None

        self.users = full.users if full else []
        self.current_user = full.current_user if full else None
        self.path = path

    def serialize(self):
        temp_path = self.path
        del self.path
        with open(temp_path, mode='w+', encoding='utf-8') as db:
            to_write = jsonpickle.encode(self, make_refs=False)
            db.write(to_write)
        self.path = temp_path

    def check_user_exist(self, nickname):
        for user in self.users:
            if user.nickname == nickname:
                raise custom_exceptions.UserAlreadyExist

    def add_user(self, new_user):
        self.check_user_exist(new_user.nickname)
        self.users.append(new_user)
        self.serialize()

    def set_current_user(self, new_current_user_nickname):
        for user in self.users:
            if user.nickname == new_current_user_nickname:
                self.current_user = new_current_user_nickname
                self.serialize()
                break
        else:
            raise custom_exceptions.UserNotFound

    def get_current_user(self):
        return self.get_users(self.current_user)

    def remove_current_user(self):
        self.current_user = None
        self.serialize()

    def remove_user(self, nickname):
        self.check_current()
        for user in self.users:
            if user.nickname == nickname:
                if self.current_user == nickname:
                    self.current_user = None
                self.users.remove(user)
                self.serialize()
                break
        else:
            raise custom_exceptions.UserNotFound

    def get_users(self, nickname=None):
        if nickname is None:
            return [user for user in self.users]
        else:
            for user in self.users:
                if user.nickname == nickname:
                    return user
            else:
                raise custom_exceptions.UserNotFound

    @staticmethod
    def get_id(list_to, sub=False):
        if sub:
            if len(list_to) == 0:
                return '1'
            else:
                pre_id = list_to[-1].id.split(const.ID_DELIMITER)
                return str(int(pre_id[-1]) + 1)
        else:
            return str(int(list_to[-1].id) + 1) if len(list_to) != 0 else '1'

    def check_current(self):
        if self.current_user:
            for user in self.users:
                if user.nickname == self.current_user:
                    return user
        else:
            raise custom_exceptions.UserNotAuthorized

    def add_plan(self, new_plan):
        current = self.check_current()
        new_plan.id = Database.get_id(current.plans)
        current.plans.append(new_plan)
        self.serialize()

    def remove_plan(self, id):
        current = self.check_current()
        current.plans.remove(self.get_plans(id))
        for task in self.get_tasks():
            if task.plan == id:
                self.remove_task(task.id)
        self.serialize()

    def get_plans(self, id=None):
        current = self.check_current()
        if id is None:
            return [plan for plan in current.plans]
        else:
            for plan in current.plans:
                if plan.id == id:
                    return plan
            else:
                raise custom_exceptions.PlanNotFound

    @staticmethod
    def rec_del_task(tasks, id):
        if len(tasks) > 0:
            for task in tasks:
                if task.id == id:
                    tasks.remove(task)
                    return
                else:
                    Database.rec_del_task(task.subtasks, id)

    @staticmethod
    def get_task_by_id(tasks, idx_mass):
        for task in tasks:
            if int(task.id.split(const.ID_DELIMITER)[-1]) == int(idx_mass[0]):
                if len(idx_mass) > 1:
                    return Database.get_task_by_id(task.subtasks, idx_mass[1:])
                else:
                    return task

    def get_tasks(self, id=None, archive=False):
        current = self.check_current()
        if id:
            found_task = Database.get_task_by_id(current.tasks, id.split(const.ID_DELIMITER))
            if found_task:
                return found_task
            else:
                raise custom_exceptions.TaskNotFound
        elif archive:
            return current.archive
        else:
            return current.tasks

    def add_task(self, new_task):
        current = self.check_current()
        if new_task.parent_id:
            parent_task = Database.get_task_by_id(current.tasks, new_task.parent_id.split(const.ID_DELIMITER))
            if parent_task:
                new_task.id = parent_task.id + const.ID_DELIMITER + Database.get_id(parent_task.subtasks, True)
                new_task.indent = new_task.id.count(const.ID_DELIMITER)
                parent_task.subtasks.append(new_task)
            else:
                raise custom_exceptions.TaskNotFound
        else:
            new_task.id = Database.get_id(current.tasks)
            current.tasks.append(new_task)
        self.serialize()

    def remove_task(self, id):
        current = self.check_current()
        Database.rec_del_task(current.tasks, id)
        self.serialize()

    def change_task(self, id, info=None, deadline=None, priority=None, status=None, plus_tag=None, minus_tag=None):
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
