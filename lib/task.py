from datetime import datetime

from lib.database import Database


class Task:
    def __init__(self, **kwargs):
        self.subtasks = []
        self.id = None
        self.info = None
        self.tags = []
        self.status = 'unfinished'
        self.deadline = None
        self.priority = 1
        self.parent_id = None
        self.indent = 0
        self.plan = None
        self.last_change = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__dict__.update(kwargs)

    def changed(self):
        self.last_change = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def finish(self):
        self.status = 'finished'
        for task in self.subtasks:
            task.status = 'finished'
            task.finish()

    def reset_sub_id(self):
        if self.subtasks:
            for task in self.subtasks:
                task.id = self.id + '_' + str(int(Database.get_id(self.subtasks, True)) - 1)
                task.indent = self.id.count('_') + 1
                task.parent_id = self.id
                Task.reset_sub_id(task)

    def append_task(self, task_from):
        task_from.id = self.id + '_' + Database.get_id(self.subtasks, True)
        task_from.indent = task_from.id.count('_')
        task_from.parent_id = self.id
        task_from.reset_sub_id()
        self.subtasks.append(task_from)
