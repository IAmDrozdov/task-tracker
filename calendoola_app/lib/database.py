import json

import jsonpickle

from calendoola_app.lib import custom_exceptions as ce
from calendoola_app.lib.constants import Constants


class Database:
    def __init__(self, path):
        """
        Class for working with database
        """
        self.path = path
        try:
            with open(self.path, mode='r', encoding='utf-8') as db:
                json_file = db.read()
            full = jsonpickle.decode(json_file)
        except json.decoder.JSONDecodeError:
            full = None
            self.create_empty()
        except FileNotFoundError:
            full = None
            self.create_empty()

        self.users = full.users if full else []
        self.current_user = full.current_user if full else None

    def create_empty(self):
        with open(self.path, mode='w', encoding='utf-8'):
            pass

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
                raise ce.UserAlreadyExists

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
        self.check_current()
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
                pre_id = list_to[-1].id.split(Constants.ID_DELIMITER)
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
            if int(task.id.split(Constants.ID_DELIMITER)[-1]) == int(idx_mass[0]):
                if len(idx_mass) > 1:
                    return Database.get_task_by_id(task.subtasks, idx_mass[1:], remove)
                else:
                    if remove:
                        tasks.remove(task)
                        return True
                    else:
                        return task

    def get_tasks(self, id=None, archive=None):
        """
        Get list of tasks or task by id or archve tasks
        :param id: id of task to return
        :param archive: if True returns archive tasks
        :return: list of tasks, archive tasks or task with this id
        """
        current = self.check_current()
        if id and archive is None:
            found_task = Database.get_task_by_id(current.tasks, id.split(Constants.ID_DELIMITER))
            if found_task:
                return found_task
            else:
                raise ce.TaskNotFound
        elif archive:
            if id is None:
                return current.archive
            else:
                for task in current.archive:
                    if task.id == id:
                        return task
        else:
            return current.tasks

    def add_task(self, new_task):
        """
        Adding task to list of currrent user tasks
        :param new_task: object of new task
        """
        current = self.check_current()
        if new_task.parent_id:
            parent_task = Database.get_task_by_id(current.tasks, new_task.parent_id.split(Constants.ID_DELIMITER))
            if parent_task is not None:
                new_task.id = parent_task.id + Constants.ID_DELIMITER + Database.get_id(parent_task.subtasks, True)
                new_task.indent = new_task.id.count(Constants.ID_DELIMITER)
                parent_task.subtasks.append(new_task)
            else:
                raise ce.TaskNotFound
        else:
            new_task.id = Database.get_id(current.tasks)
            current.tasks.append(new_task)
        self.serialize()

    def remove_task(self, id, archive=None):
        """
        remove task from current user tasks
        :param archive: remove from archive if "true"
        :param id: id of task to delete
        """
        current = self.check_current()
        if not archive:
            if not Database.get_task_by_id(current.tasks, id.split(Constants.ID_DELIMITER), True):
                raise ce.TaskNotFound
        else:
            to_remove = self.get_tasks(id, True)
            if to_remove:
                current.archive.remove(to_remove)
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
        task = self.get_tasks(id)
        task.change(info=info, deadline=deadline, priority=priority, status=status, plus_tag=plus_tag,
                    minus_tag=minus_tag)
        if hasattr(task, 'owner'):
            owner = self.get_users(task.owner['nickname'])
            task_owner = Database.get_task_by_id(owner.tasks, id.split(Constants.ID_DELIMITER))
            task_owner.change(info=info, deadline=deadline, priority=priority, status=status, plus_tag=plus_tag,
                              minus_tag=minus_tag)

        if hasattr(task, 'user'):
            user = self.get_users(task.user['nickname'])
            task_user = Database.get_task_by_id(user.tasks, id.split(Constants.ID_DELIMITER))
            task_user.change(info=info, deadline=deadline, priority=priority, status=status, plus_tag=plus_tag,
                             minus_tag=minus_tag)
        self.serialize()
