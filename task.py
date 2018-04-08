from datetime import datetime
import datetime_parser
import database
from colorama import Fore


class Task:

    def __init__(self, *initial_data, **kwargs):
        """
        :param kwargs:
        name = name of task
        data = date of create
        """
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        self.subtasks = []
        self.indent = 0
        self.status = 'unfinished'
        self.deadline = None
        self.date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.__dict__.update(kwargs)

    def _table_print(self):
        pass

    @staticmethod
    def add_subtask(task_parent, task_child):
        task_parent.subtasks.append(task_child)

    @staticmethod
    def print(container, id=None, tag=None, is_colored=True):
        if is_colored:
            priority_colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.LIGHTMAGENTA_EX, Fore.RED]
        else:
            priority_colors = [Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE]

        if id:
            for index, task in enumerate(container):
                if task.id == id:
                    if task.deadline is None:
                        deadline_print = 'no deadline'
                    else:
                        deadline_print = datetime_parser.parse_iso_pretty(task.deadline)
                    print('#', index+1, '|', task.info, '|', task.id, '|', task.status, '|',
                          datetime_parser.parse_iso_pretty(task.date), '|', deadline_print)
                    if len(task.subtasks) > 0:
                        for index_s, sub in enumerate(task.subtasks):
                            if sub.deadline is None:
                                deadline_print_sub = 'no deadline'
                            else:
                                deadline_print_sub = datetime_parser.parse_iso_pretty(sub.deadline)
                            print(sub.indent*'  ', '#', index_s + 1, '|', sub.info, '|', sub.id, '|',
                                  sub.status, '|', datetime_parser.parse_iso_pretty(sub.date), '|', deadline_print_sub)

                    break
            else:
                print('Nothing to show')
        elif tag:
            is_empty = True
            for index, task in enumerate(container):
                if tag in task.tags:
                    is_empty = False
                    if task.deadline is None:
                        deadline_print = 'no deadline'
                    else:
                        deadline_print = datetime_parser.parse_iso_pretty(task.deadline)
                    print('#', index+1, '|', task.info, '|', task.id, '|', task.status, '|',
                          datetime_parser.parse_iso_pretty(task.date), '|', deadline_print)

            if is_empty is True:
                print('Nothing to Show')

        else:
            for index, task in enumerate(container):
                deadline_print = datetime_parser.parse_iso_pretty(task.deadline) if task.deadline else 'no deadline'
                print(priority_colors[task.priority-1] + '#', index+1, '|', task.info, '|', task.id, '|',
                      task.status, '|', datetime_parser.parse_iso_pretty(task.date), '|', deadline_print)

    @staticmethod
    def delete(container, id):
        for task in container:
            if task.id == id:
                container.remove(task)
                database.serialize(container, 'database_tasks.json')
                break
        else:
            print('nothing to delete')

    @staticmethod
    def change_status(task, status_new='finished'):
        task.status = status_new
        if task.subtasks != 0:
            for sub in task.subtasks:
                sub.status = status_new
