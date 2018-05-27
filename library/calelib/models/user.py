import copy

import calelib.etc.custom_exceptions as ce
from calelib.db.database import Database
from calelib.modules.constants import Constants
from calelib.modules.logger import logg


class User:
    def __init__(self, nickname):
        self.nickname = nickname
        self.tasks = []
        self.plans = []
        self.archive = []

    @logg('Task replaced to archive')
    def archive_task(self, task_id):
        """
         Add finished task to archive
        :param task_id: id of task to archive
        :return:
        """
        task_to_remove = Database.get_task_by_id(self.tasks, self.__split_id(task_id))
        task_to_archive = copy.deepcopy(task_to_remove)
        task_to_archive.id = Database.get_id(self.archive)
        self.archive.append(task_to_archive)
        self.remove_task(task_to_remove.id)

    @staticmethod
    def __split_id(id: str):
        return id.split(Constants.ID_DELIMITER)

    @logg('Task appended to User')
    def add_task(self, new_task):
        """
        add task to 'tasks'
        :param new_task: instance
        """
        if new_task.parent_id:
            parent_task = Database.get_task_by_id(self.tasks, self.__split_id(new_task.parent_id))
            if parent_task is not None:
                new_task.id = parent_task.id + Constants.ID_DELIMITER + Database.get_id(parent_task.subtasks, True)
                new_task.indent = new_task.id.count(Constants.ID_DELIMITER)
                parent_task.subtasks.append(new_task)
            else:
                raise ce.TaskNotFound
        else:
            new_task.id = Database.get_id(self.tasks)
            self.tasks.append(new_task)

    @logg('Task removed from User')
    def remove_task(self, id, archive=None):
        """
        Remove task from 'tasks'
        :param id: task's to remove id
        :param archive: if True search in 'archive'
        """
        if not archive:
            if not Database.get_task_by_id(self.tasks, self.__split_id(id), True):
                raise ce.TaskNotFound
        else:
            for archived in self.archive:
                if archived.id == id:
                    self.archive.remove(archived)
                    break
                else:
                    raise ce.TaskNotFound

    def get_task(self, id, archive=None):
        """
        Get task
        :param id: id of task to get
        :param archive: if True search in 'archive'
        :return: task
        """
        task = None
        if not archive:
            task = Database.get_task_by_id(self.tasks, self.__split_id(id))
        else:
            for archived_task in self.archive:
                if archived_task.id == id:
                    task = archived_task
        if task is None:
            raise ce.TaskNotFound
        else:
            return task

    def get_all_tasks(self, archive=None):
        """
        Return list of tasks
        :param archive: if True return 'archive' list
        :return: list of tasks
        """
        if archive:
            return self.archive
        else:
            return self.tasks

    @logg('Plan appended to User')
    def add_plan(self, new_plan):
        """
        Add plan to 'plans'
        :param new_plan: instance
        """
        new_plan.id = Database.get_id(self.plans)
        self.plans.append(new_plan)

    @logg('Plan removed from User')
    def remove_plan(self, id):
        """
        Remove plan from 'plans'
        :param id: id of plan to remove
        """
        self.plans.remove(self.get_plan(id))
        for task in self.get_all_tasks():
            if task.plan == id:
                self.remove_task(task.id)
                break

    def get_plan(self, id):
        """
        Get plan by id
        :param id: id of plan to get
        """
        for plan in self.plans:
            if plan.id == id:
                return plan
        else:
            raise ce.PlanNotFound

    def get_all_plans(self):
        """
        Return 'plans'
        :return: list of plans
        """
        return self.plans
