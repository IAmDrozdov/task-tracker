from lib.task import Task
from lib import database


class TaskContainer:
    def __init__(self):
        self.list = database.deserialize('database_tasks.json')
