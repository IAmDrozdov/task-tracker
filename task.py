from datetime import datetime
import datetime_parser
import database
from colorama import Fore


class Task:

    def __init__(self, **kwargs):
        """
        :param kwargs:
        name = name of task
        data = date of create
        """
        self.subtasks = []
        self.id = None
        self.info = None
        self.tags = []
        self.status = 'unfinished'
        self.deadline = None
        self.priority = 1
        self.date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.__dict__.update(kwargs)

    def table_print(self, index, color=False):
        if color:
            priority_colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.LIGHTMAGENTA_EX, Fore.RED]
        else:
            priority_colors = [Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE]
        deadline_print = datetime_parser.parse_iso_pretty(self.deadline) if self.deadline else 'no deadline'
        print(priority_colors[self.priority-1] + '#', index + 1, '|', self.info, '|', self.id, '|', self.status, '|',
              datetime_parser.parse_iso_pretty(self.date), '|', deadline_print)

    @staticmethod
    def print(container, id=None, tag=None, is_colored=True):
        if id:
            for index, task in enumerate(container):
                if task.id == id:
                    task.table_print(index)
                    if len(task.subtasks) > 0:
                        for index_s, sub in enumerate(task.subtasks):
                            print(sub.indent*'  ', end='')
                            sub.table_print(index_s)

                    break
            else:
                print('Nothing to show')
        elif tag:
            is_empty = True
            for index, task in enumerate(container):
                if tag in task.tags:
                    is_empty = False
                    task.table_print(index)
            if is_empty is True:
                print('Nothing to Show')

        else:
            for index, task in enumerate(container):
                task.table_print(index, is_colored)

    @staticmethod
    def delete(container, id):
        for task in container:
            if task.id == id:
                container.remove(task)
                database.serialize(container, 'database_tasks.json')
                break
        else:
            print('nothing to delete')

    def change_status(self, status_new='finished'):
        self.status = status_new
        if '_' not in self.id:
            if self.subtasks != 0:
                for sub in self.subtasks:
                    sub.status = status_new
        else:
            pass
