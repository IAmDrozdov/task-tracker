import copy


class User:
    def __init__(self):
        self.nickname = None
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
                self.archive.append(copy.deepcopy(task))
                self.tasks.remove(task)
                return
