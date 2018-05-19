import copy

from calendoola_app.lib.database import Database


class User:
    def __init__(self, nickname):
        self.nickname = nickname
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
                task.id = Database.get_id(self.archive)
                self.archive.append(copy.deepcopy(task))
                self.tasks.remove(task)
                return
