import re


class User:
    def __init__(self, **kwargs):
        self.nickname = None
        self.tasks = []
        self.plans = []
        self.archive = []
        self.mail = None
        self.__dict__.update(**kwargs)

    def print(self):
        tasks_print = []
        for task in self.tasks:
            tasks_print.append(task.info)
        print(self.nickname, '|', ', '.join(tasks_print))