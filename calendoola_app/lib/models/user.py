import copy

import calendoola_app.lib.custom_exceptions as ce
from calendoola_app.lib.constants import Constants
from calendoola_app.lib.database import Database


class User:
    def __init__(self, nickname):
        self.nickname = nickname
        self.tasks = []
        self.plans = []
        self.archive = []

    def archive_task(self, task_id):
        """
         Add finished task to archive
        :param task_id: id of task to archive
        :return:
        """
        for task in self.tasks:
            if task.id == task_id:
                task.id = Database.get_id(self.archive)
                self.archive.append(copy.deepcopy(task))
                self.tasks.remove(task)
                return

    @staticmethod
    def __split_id(id: str):
        return id.split(Constants.ID_DELIMITER)

    def add_task(self, new_task):
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

    def remove_task(self, id, archive=None):
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
        if archive:
            return self.archive
        else:
            return self.tasks

    def add_plan(self, new_plan):
        new_plan.id = Database.get_id(self.plans)
        self.plans.append(new_plan)

    def remove_plan(self, id):
        self.plans.remove(self.get_plan(id))
        for task in self.get_all_tasks():
            if task.plan == id:
                self.remove_task(task.id)
                break

    def get_plan(self, id):
        for plan in self.plans:
            if plan.id == id:
                return plan
        else:
            raise ce.PlanNotFound

    def get_all_plans(self):
        return self.plans
