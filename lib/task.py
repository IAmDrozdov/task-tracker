from datetime import datetime
from lib import datetime_parser
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
        self.indent = 0
        self.plan = None
        self.changed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__dict__.update(kwargs)

    def table_print(self, color=False):
        if color:
            priority_colors = [Fore.CYAN, Fore.GREEN, Fore.YELLOW, Fore.LIGHTMAGENTA_EX, Fore.RED]
        else:
            priority_colors = [Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE, Fore.WHITE]

        deadline_print = datetime_parser.parse_iso_pretty(self.deadline) if self.deadline else 'no deadline'
        offset = '+' if self.indent == 0 else self.indent*' ' + self.indent*' *'
        date_print = datetime_parser.parse_iso_pretty(self.date)
        tags_print = ' '.join(self.tags)
        print(priority_colors[self.priority - 1] + offset, self.info, self.id, self.status, date_print, deadline_print,
              tags_print)

    @staticmethod
    def get_actual_index(container, is_sub=True):
        if is_sub:
            if len(container) == 0:
                return '1'
            else:
                pre_id = container[len(container) - 1].id.split('_')
                return str(int(pre_id[len(pre_id) - 1]) + 1)
        else:
            return str(int(container[len(container) - 1].id) + 1) if len(container) != 0 else '1'
