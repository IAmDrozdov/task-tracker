from lib.task import Task
from datetime import datetime


class Plan:
    def __init__(self, **kwargs):
        self.info = ''
        self.is_created = False
        self.last_create = None
        self.period = None
        self.id = None
        self.__dict__.update(**kwargs)

    def create_task(self):
        new_task = Task(info=self.info, plan=self.id)
        self.is_created = True
        self.last_create = ' '.join([str(datetime.now().hour), str(datetime.now().day), str(datetime.now().month)])
        return new_task

    def is_mine(self, task):
        if hasattr(task, 'plan'):
            if task.plan == self.id:
                return task

    def check(self, container):
        for task in container:
            self.is_mine(task)

    def is_done(self, task):
        pass