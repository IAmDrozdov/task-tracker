from datetime import datetime

from lib.constants import Constants as const
from lib.database import Database
import lib.datetime_parser as dp
import re


class Task:
    def __init__(self, **kwargs):
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
        self.info = None
        self.tags = []
        self.status = const.STATUS_UNFINISHED
        self.deadline = None
        self.priority = 1
        self.parent_id = None
        self.indent = 0
        self.plan = None
        self.last_change = datetime.now().strftime(const.DATE_PATTERN)
        self.date = datetime.now().strftime(const.DATE_PATTERN)
        self.__dict__.update(kwargs)

    def changed(self):
        """
        Updating field last_cgange
        """
        self.last_change = datetime.now().strftime(const.DATE_PATTERN)

    def finish(self):
        """
        Finish self and all subtasks
        """
        self.status = const.STATUS_FINISHED
        for task in self.subtasks:
            task.finish()

    def unfinish(self):
        """
         Unfinish self and all subtasks
         """
        self.status = const.STATUS_UNFINISHED
        for task in self.subtasks:
            task.finish()

    def reset_sub_id(self):
        """
        Updates subtasks id dependents on self
        """
        if self.subtasks:
            for task in self.subtasks:
                task.id = self.id + const.ID_DELIMITER + str(int(Database.get_id(self.subtasks, True)) - 1)
                task.indent = self.id.count(const.ID_DELIMITER) + 1
                task.parent_id = self.id
                Task.reset_sub_id(task)

    def append_task(self, task_from):
        """
        Adding task_from to self subtasks
        :param task_from: task to attach to self
        """
        task_from.id = self.id + const.ID_DELIMITER + Database.get_id(self.subtasks, True)
        task_from.indent = task_from.id.count(const.ID_DELIMITER)
        task_from.parent_id = self.id
        task_from.reset_sub_id()
        self.subtasks.append(task_from)

    def change(self, info=None, deadline=None, priority=None, status=None, plus_tag=None, minus_tag=None):
        if info:
            self.info = info
        if deadline:
            self.deadline = dp.get_deadline(deadline)
        if priority:
            self.priority = priority
        if status == const.STATUS_FINISHED:
            self.finish()
        else:
            self.status = status
        if plus_tag:
            for tag in re.split("[^\w]", plus_tag):
                self.tags.append(tag)
            self.tags = list(set(self.tags))
        if minus_tag:
            for tag in re.split("[^\w]", minus_tag):
                self.tags.remove(tag)
        self.changed()
