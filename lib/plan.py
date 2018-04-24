from lib.task import Task
from datetime import datetime
from colorama import Fore


class Plan:
    def __init__(self, **kwargs):
        self.info = ''
        self.is_created = False
        self.last_create = ' '.join([str(datetime.now().hour), str(datetime.now().day), str(datetime.now().month)])
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

    def is_done(self, task):
        return True if task.find_plan(self).is_created else False

    def __str__(self):
        created = '\nstatus: created' if self.is_created else '\nstatus: not created'
        return ' '.join(['Info:', self.info, '\nID:', self.id, created, self.last_create])

    def colored_print(self, colored):
        if colored:
            color = Fore.LIGHTCYAN_EX if self.is_created else Fore.RED
        else:
            color = Fore.WHITE
        print(color + self.info, self.id)

    def delta_check(self):

        pass

    @staticmethod
    def check(container):
        for plan in container:
            if not plan.is_created:
                plan.delta_check()
