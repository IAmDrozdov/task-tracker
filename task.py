from datetime import datetime
import datetime_parser
import database
from colorama import Fore


class Task:
    priority = None
    comments = []
    tags = []
    isComplex = False
    subtasks = []

    def __init__(self, **kwargs):
        """
        :param kwargs:
        name = name of task
        data = date of create
        """
        self.status = 'unfinished'
        self.deadline = None
        self.date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.__dict__.update(kwargs)

    def _table_print(self):
        pass

    @staticmethod
    def print(container, id=None, tag=None):
        priority_colors = [Fore.CYAN,
                           Fore.GREEN,
                           Fore.YELLOW,
                           Fore.LIGHTMAGENTA_EX,
                           Fore.RED]
        if id:
            for index, task in enumerate(container):
                if task['id'] == id:
                    date_print = datetime_parser.date_print(task['date'])
                    if task['deadline'] is None:
                        deadline_print = 'no deadline'
                    else:
                        deadline_print = datetime_parser.date_print(task['deadline'])
                    print('#', index+1, '|', task['info'], '|', task['id'], '|', task['status'], '|', date_print
                          , '|', deadline_print)
                    break
            else:
                print('Nothing to show')
        elif tag:
            is_empty = True
            for index, task in enumerate(container):
                if tag in task['tags']:
                    is_empty = False
                    date_print = datetime_parser.date_print(task['date'])
                    if task['deadline'] is None:
                        deadline_print = 'no deadline'
                    else:
                        deadline_print = datetime_parser.date_print(task['deadline'])
                    print('#', index+1, '|', task['info'], '|', task['id'], '|', task['status'], '|', date_print
                          , '|', deadline_print)

            if is_empty is True:
                print('Nothing to Show')


        else:
            for index, task in enumerate(container):
                date_print = datetime_parser.date_print(task['date'])
                deadline_print = datetime_parser.date_print(task['deadline']) if task['deadline'] else 'no deadline'

                print(priority_colors[task['priority']-1] + '#', index+1, '|', task['info'], '|', task['id'], '|',
                      task['status'], '|', date_print, '|', deadline_print)


    @staticmethod
    def delete(container, id):
        for task in container:
            if task['id'] == id:
                container.remove(task)
                database.serialize(container, 'database_tasks.json')
                break
        else:
            print('nothing to delete')

    def change_status(self, status_new):
        self.status = status_new
