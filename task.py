from datetime import datetime


class Task:
    def __init__(self, **kwargs):
        """
        :param kwargs:
        name = name of task
        data = date of create
        """
        self.status = 'unfinished'
        self.date = datetime.now()
        self.__dict__.update(kwargs)
