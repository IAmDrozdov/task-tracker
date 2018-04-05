from datetime import datetime
import datetime_parser
import database


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
    def print(container, id=None):
        if id is None:
            for index, task in enumerate(container):
                date_print = datetime_parser.date_print(task['date'])
                if task['deadline'] is None:
                    deadline_print = 'no deadline'
                else:
                    deadline_print = datetime_parser.date_print(task['deadline'])
                print('#', index+1, '|', task['info'], '|', task['id'], '|', task['status'], '|', date_print
                      , '|', deadline_print)
        else:
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


