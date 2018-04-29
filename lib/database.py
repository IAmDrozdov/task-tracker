import jsonpickle
import json
import re
from lib import datetime_parser
from lib import custom_exceptions


def serialize(container, path):
        with open(path, mode='w+', encoding='utf-8') as db:
            to_write = jsonpickle.encode(container)
            db.write(to_write)


def deserialize(path):
    try:
        with open(path, mode='r', encoding='utf-8') as db:
            json_file = db.read()
        return jsonpickle.decode(json_file)
    except json.decoder.JSONDecodeError:
        return {'current_user': None,
                'users': []}
    except FileNotFoundError:
        with open(path, mode='w+', encoding='utf-8') as db:
            db.write(jsonpickle.encode(({'current_user': None,
                                       'users': []})))
        with open(path, mode='r', encoding='utf-8') as db:
            json_file = db.read()
        return jsonpickle.decode(json_file)


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
            to_write = jsonpickle.encode(self)
            db.write(to_write)
        self.path = temp_path

    def check_user_exist(self, new_user_nickname):
        for user in self.users:
            if user.nickname == new_user_nickname:
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

    def remove_current_user(self):
        self.current_user = None
        self.serialize()

    def remove_user(self, user_nickname):
        for user in self.users:
            if user.nickname == user_nickname:
                if self.current_user == user_nickname:
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

    def check_current(self):
        if self.current_user:
            for user in self.users:
                if user.nickname == self.current_user:
                    return user
        else:
            raise custom_exceptions.UserNotAuthorized

    def add_plan(self, new_plan):
        current = self.check_current()
        current.plans.append(new_plan)
        self.serialize()

    def remove_plan(self, id):
        current = self.check_current()
        current.plans.remove(self.get_plans(id))
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
                else:
                    Database.rec_del_task(task.subtasks, id)

    @staticmethod
    def rec_get_task(tasks, id):
        if len(tasks) > 0:
            for task in tasks:
                if task.id == id:
                    return task
                else:
                    return Database.rec_get_task(task.subtasks, id)

    def get_tasks(self, id=None):
        current = self.check_current()
        if id is None:
            return [task for task in current.tasks]
        else:
            found_task = Database.rec_get_task(current.tasks, id)
            if found_task:
                return found_task
            else:
                raise custom_exceptions.TaskNotFound

    def add_task(self, new_task):
        current = self.check_current()
        if new_task.parent_id:
            found_task = Database.rec_get_task(current.tasks, new_task.parent_id)
            if found_task:
                found_task.subtasks.append(new_task)
            else:
                raise custom_exceptions.TaskNotFound
        else:
            current.tasks.append(new_task)
        self.serialize()

    def remove_task(self, id):
        current = self.check_current()
        Database.rec_del_task(current.tasks, id)
        self.serialize()

    def change_task(self, id, info=None, deadline=None, priority=None, status=None, plus_tag=None, minus_tag=None):
        found_task = self.get_tasks(id)
        if info:
            found_task.info = info
        if deadline:
            found_task.deadline = datetime_parser.get_deadline(deadline)
        if priority:
            found_task.priority = priority
        if status:
            found_task.status = status
        if plus_tag:
            for tag in re.sub("[^\w]", " ", plus_tag).split():
                found_task.tags.append(tag)
            found_task.tags = list(set(found_task.tags))
        if minus_tag:
            for tag in re.sub("[^\w]", " ", plus_tag).split():
                found_task.tags.remove(tag)
        found_task.changed()
