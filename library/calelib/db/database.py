import json

import jsonpickle
from calelib.etc.custom_exceptions import UserNotAuthorized, UserAlreadyExists, UserNotFound
from calelib.modules.constants import Constants
from calelib.modules.logger import logg


class Database:
    def __init__(self, path):
        """
        Interface for working with database
        """
        self.path = path
        try:
            with open(self.path, mode='r', encoding='utf-8') as db:
                json_file = db.read()
            full = jsonpickle.decode(json_file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            full = None
            self.create_empty()

        self.users = full.users if full else []
        self.current_user = full.current_user if full else None

    @logg('Created empty database')
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
                raise UserAlreadyExists

    @logg('Created new User')
    def add_user(self, new_user):
        """
        Adding new user in database
        :param new_user: object of new user
        """
        self.check_user_exist(new_user.nickname)
        self.users.append(new_user)
        self.serialize()

    @logg('Changed current user')
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
            raise UserNotFound

    def get_current_user(self):
        """
        Get current user object
        :return: current user object
        """
        return self.check_current()

    @logg('Removed current user')
    def remove_current_user(self):
        """
        Remove current user
        """
        self.current_user = None
        self.serialize()

    @logg('Removed User')
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
            raise UserNotFound

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
                raise UserNotFound

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
            raise UserNotAuthorized

    @logg('Created Plan')
    def add_plan(self, new_plan):
        """
        Append plan to current user plans
        :param new_plan:
        """
        current = self.check_current()
        current.add_plan(new_plan)
        self.serialize()

    @logg('Removed Plan')
    def remove_plan(self, id):
        """
        Removes plan from current user plans
        :param id: id of plan to remove
        """
        current = self.check_current()
        current.remove_plan(id)
        self.serialize()

    def get_plans(self, id=None):
        """
        Get plan object  via ID or all
        :param id: id of plan to return
        :return: list of plans or plan with this id
        """
        current = self.check_current()
        return current.get_all_plans() if id is None else current.get_plan(id)

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
        if id:
            return current.get_task(id, archive)
        else:
            return current.get_all_tasks(archive)

    @logg('Created new Task')
    def add_task(self, new_task):
        """
        Adding task to list of currrent user tasks
        :param new_task: object of new task
        """
        current = self.check_current()
        current.add_task(new_task)
        self.serialize()

    @logg('Removed Task')
    def remove_task(self, id, archive=None):
        """
        remove task from current user tasks
        :param archive: remove from archive if "true"
        :param id: id of task to delete
        """
        current = self.check_current()
        current.remove_task(id, archive)
        self.serialize()

    @logg('Changed information about Task')
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
        current = self.check_current()
        task = current.get_task(id)
        task.change(info=info, deadline=deadline, priority=priority, status=status, plus_tag=plus_tag,
                    minus_tag=minus_tag)
        if task.owner:
            owner = self.get_users(task.owner['nickname'])
            task_owner = owner.get_task(task.owner['id'])
            task_owner.change(info=info, deadline=deadline, priority=priority, status=status, plus_tag=plus_tag,
                              minus_tag=minus_tag)

        if task.user:
            user = self.get_users(task.user['nickname'])
            task_user = user.get_task(task.user['id'])
            task_user.change(info=info, deadline=deadline, priority=priority, status=status, plus_tag=plus_tag,
                             minus_tag=minus_tag)
        self.serialize()
