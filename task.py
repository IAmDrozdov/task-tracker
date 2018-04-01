from datetime import datetime


class Task:
    counter = 0

    def __init__(self, **kwargs):
        """
        :param kwargs:
        name = name of task
        data = date of create
        """
        self.date = datetime.now().strftime('%d-%m-%y')
        self.__dict__.update(kwargs)
