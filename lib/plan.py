from lib.task import Task
from datetime import datetime, timedelta
from colorama import Fore
import lib.datetime_parser as dp


class Plan:
    def __init__(self, **kwargs):
        self.info = ''
        self.is_created = False
        self.last_create = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_in = None
        self.period_type = None
        self.next_create = None
        self.id = None
        self.period = None
        self.__dict__.update(**kwargs)
        if self.period_type == 'd':
            self.next_create = (dp.parse_iso(self.last_create) + timedelta(days=int(self.period)))\
                .strftime("%Y-%m-%d %H:%M:%S")

    def create_task(self):
        new_task = Task(info=self.info, plan=self.id, id=self.id+'_p')
        self.is_created = True
        self.last_create = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.inc_next() if self.period_type == 'd' else None
        return new_task

    def is_mine(self, task):
        if hasattr(task, 'plan'):
            return True if task.plan == self.id else False

    def __str__(self):
        created = '\nstatus: created' if self.is_created else '\nstatus: not created'
        return ' '.join(['Info:', self.info, '\nID:', self.id, created, self.last_create])

    def colored_print(self, colored):
        if colored:
            color = Fore.LIGHTCYAN_EX if self.is_created else Fore.RED
        else:
            color = Fore.WHITE
        print(color + self.info, self.id)

    def check_before_create(self):
        if self.period_type == 'd':
            if self.delta_period_next() == timedelta(days=0):
                if int(self.time_in) <= datetime.now().hour:
                    return True

    def delta_period_next(self):
        return dp.parse_iso(self.next_create) - datetime.now().date()

    def delta_period_last(self):
        return dp.parse_iso(self.last_create) - datetime.now().date()

    def inc_next(self):
        self.next_create = (dp.parse_iso(self.last_create) + timedelta(days=self.period)).strftime("%Y-%m-%d %H:%M:%S")

    def check_uncreated_days(self, container):
        if self.check_before_create():
            container.append(self.create_task())
            self.is_created = True
        return

    def check_uncreated_wdays(self, container):
        for wday in self.period:
            if datetime.now().weekday() == wday:
                if int(self.time_in) <= datetime.now().hour:
                    container.append(self.create_task())
                    self.is_created = True
                    return

    def check_created_days(self, container):
        if self.delta_period_last() != timedelta(days=0):
            self.is_created = False
            for task in container:
                if self.is_mine(task):
                    container.remove(task)
                    return

    def check_created_wdays(self, container):
        for wday in self.period:
            if datetime.now().weekday() != wday:
                self.is_created = False
                for task in container:
                    if self.is_mine(task):
                        container.remove(task)
                return

    def check(self, container):
        if not self.is_created:
            self.check_uncreated_days(container) if self.period_type == 'd' else self.check_uncreated_wdays(container)
        else:
            self.check_created_days(container) if self.period_type == 'd' else self.check_created_wdays(container)
