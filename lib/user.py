import copy


class User:
    def __init__(self, **kwargs):
        self.nickname = None
        self.tasks = []
        self.plans = []
        self.archive = []
        self.__dict__.update(kwargs)

    def archive_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                self.archive.append(copy.deepcopy(task))
                self.tasks.remove(task)
                return
