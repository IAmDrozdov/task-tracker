from task import Task


class TaskContainer:
    tasks = []

    def __init__(self):
        pass

    def push(self, new_task):
        self.tasks.append(new_task)

