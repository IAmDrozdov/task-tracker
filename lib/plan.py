from lib.task import Task
from datetime import datetime, timedelta
from colorama import Fore
from lib.database import Database
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

    def __str__(self):
        created = '\nstatus: created' if self.is_created else '\nstatus: not created'
        return ' '.join(['Info:', self.info, '\nID:', self.id, created])

    def colored_print(self, colored):
        if colored:
            color = Fore.LIGHTCYAN_EX if self.is_created else Fore.RED
        else:
            color = Fore.WHITE
        print(color + self.info, self.id)

    def create_task(self):
        new_task = Task(info=self.info, plan=self.id, id=self.id + '_p')
        self.is_created = True
        self.last_create = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.inc_next() if self.period_type == 'd' else None
        return new_task

    def check_uncreated(self):
        if self.period_type == 'd':
            if self.delta_period_next() != timedelta(days=0):
                if self.time_in:
                    if int(self.time_in) > datetime.now().hour:
                        return
                return
        else:
            for wday in self.period:
                if datetime.now().weekday() == wday:
                    if self.time_in:
                        if int(self.time_in) > datetime.now().hour:
                            return
                    return
        return self.create_task()

    def delta_period_next(self):
        return dp.parse_iso(self.next_create) - datetime.now().date()

    def delta_period_last(self):
        return dp.parse_iso(self.last_create) - datetime.now().date()

    def inc_next(self):
        self.next_create = (dp.parse_iso(self.last_create) + timedelta(days=int(self.period)))\
            .strftime("%Y-%m-%d %H:%M:%S")

    def check_created(self, tasks):
        if self.period_type == 'd':
            return self.check_created_days(tasks)
        else:
            return self.check_created_wdays(tasks)

    def is_mine(self, task):
        if hasattr(task, 'plan'):
            return True if task.plan == self.id else False

    def check_created_days(self, tasks):
        if self.delta_period_last() != timedelta(days=0):
            self.is_created = False
            for task in tasks:
                if self.is_mine(task):
                    print(task)
                    return task

    def check_created_wdays(self, tasks):
        for wday in self.period:
            if datetime.now().weekday() != wday:
                self.is_created = False
                for task in tasks:
                    if self.is_mine(task):
                        return task

    def check(self, database):
        if not self.is_created:
            to_add = self.check_uncreated()
            if to_add:
                database.add_task(to_add)
            else:
                return
        else:
            to_remove = self.check_created(database.get_tasks())
            database.remove_task(to_remove)
