import re
from datetime import datetime

from calelib.db.database import Database
from calelib.etc.custom_exceptions import CycleError
from calelib.etc.dates import parse_iso
from calelib.modules.constants import Status, Constants
from calelib.modules.logger import logg
from calelib.modules.notification import call


class Task:
    def __init__(self, info=None, priority=1, deadline=None, tags=None, parent_id=None, plan=None):
        """
        :param subtasks: list of subtasks
        :param id: id of task
        :param info: information about task
        :param tags: list of tags
        :param status: status of implementation
        :param deadline: date when task is not actual
        :param priority: priority of task
        :param parent_id:  id of parent task
        :param indent: dependents on level of subtask
        :param plan: id of plan what has been created task
        :param date: date when task has been created
        """
        self.subtasks = []
        self.id = None
        self.info = info
        self.tags = tags
        self.status = Status.UNFINISHED
        self.deadline = deadline
        self.priority = priority
        self.parent_id = parent_id
        self.indent = 0
        self.user = None
        self.owner = None
        self.plan = plan
        self.last_change = datetime.now().strftime(Constants.DATE_PATTERN)
        self.date = datetime.now().strftime(Constants.DATE_PATTERN)

    def __changed(self):
        """
        Updating field last_cgange
        """
        self.last_change = datetime.now().strftime(Constants.DATE_PATTERN)

    @logg('Finished Task')
    def finish(self):
        """
        Finish self and all subtasks
        """
        self.status = Status.FINISHED
        for task in self.subtasks:
            task.finish()

    @logg('Unfinished Task')
    def unfinish(self):
        """
         Unfinish self and all subtasks
         """
        self.status = Status.UNFINISHED
        for task in self.subtasks:
            task.finish()

    @logg('''Changed subtask's IDs''')
    def reset_sub_id(self):
        """
        Updates subtasks id dependents on self
        """
        if self.subtasks:
            for task in self.subtasks:
                task.id = self.id + Constants.ID_DELIMITER + str(int(Database.get_id(self.subtasks, True)) - 1)
                task.indent = self.id.count(Constants.ID_DELIMITER) + 1
                task.parent_id = self.id
                Task.reset_sub_id(task)

    @logg('Appended Task to Task')
    def append_task(self, task_from):
        """
        Adding task_from to self subtasks
        :param task_from: task to attach to self
        """
        task_from.id = self.id + Constants.ID_DELIMITER + Database.get_id(self.subtasks, True)
        task_from.indent = task_from.id.count(Constants.ID_DELIMITER)
        task_from.parent_id = self.id
        task_from.reset_sub_id()
        self.subtasks.append(task_from)

    def change(self, info=None, deadline=None, priority=None, status=None, plus_tag=None, minus_tag=None):
        """
        Change information about task
        """
        if info:
            self.info = info
        if deadline:
            self.deadline = deadline
        if priority:
            self.priority = priority
        if status == Status.FINISHED:
            self.finish()
        elif status:
            self.status = status
        if plus_tag:
            for tag in filter(None, re.split("[^\w]", plus_tag)):
                self.tags.append(tag)
            self.tags = list(set(self.tags))
        if minus_tag:
            for tag in filter(None, re.split("[^\w]", minus_tag)):
                self.tags.remove(tag)
        self.__changed()

    @logg('Task checked for overdue')
    def check(self, db):
        """
        Check task deadline for overdue
        :param db: container what has this task
        """
        if self.deadline:
            if parse_iso(self.deadline) < datetime.now().date() and self.status == Status.UNFINISHED:
                self.status = Status.OVERDUE
                call(self.info, 'Lost deadline')
                db.get_current_user().archive_task(self.id)
                db.serialize()

    @logg('Added owner to Task')
    def add_owner(self, nickname, id):
        """
        add owner to task
        :param nickname: owner's nickname
        :param id: task's id in user's tasks
        """
        self.owner = {'nickname': nickname, 'id': id}

    @logg('Added user to Task')
    def add_user(self, nickname, id):
        """
        add user to task
        :param nickname: user's nickname
        :param id: task's id in user's tasks
        """
        self.user = {'nickname': nickname, 'id': id}

    @logg('Removed user from Task')
    def remove_user(self):
        """
        Remove user from task
        """
        self.user = None

    def __rec_up(self, id):
        for task in self.subtasks:
            if task.id == id:
                return True
            else:
                task.__rec_up(id)

    def is_parent(self, id):
        """
        check task for be parent of task
        :param task_to: task what checing
        :return: True if task_to is parent of current task, else False
        """
        if self.__rec_up(id):
            raise CycleError
        else:
            return False
