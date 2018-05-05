from datetime import datetime, timedelta

import calendoola_app.lib.datetime_parser as dp
from calendoola_app.lib.constants import Constants as const
from calendoola_app.lib.notification import call
from calendoola_app.lib.models.task import Task


class Plan:
    def __init__(self, **kwargs):
        """
        Core that create tasks dependents on time
        :param info: information about task
        :param is_created: status of creating task
        :param last_create: date of last create
        :param time_at: time when task should be created
        :param period_type: type of period (daily or weekday)
        :param next_create: for daily tasks keep info when should be created next time
        :param id: id of plan
        :param petiod: period of creating task
        """
        self.info = ''
        self.is_created = False
        self.last_create = datetime.now().strftime(const.DATE_PATTERN)
        self.time_at = None
        self.period_type = None
        self.next_create = None
        self.id = None
        self.period = None
        self.__dict__.update(**kwargs)
        if self.period_type == const.REPEAT_DAY:
            self.next_create = (dp.parse_iso(self.last_create) + timedelta(days=int(self.period))) \
                .strftime(const.DATE_PATTERN)

    def create_task(self):
        """
        Create new task
        :return: task object
        """
        new_task = Task(info=self.info, plan=self.id)
        self.is_created = True
        self.last_create = datetime.now().strftime(const.DATE_PATTERN)
        self.inc_next() if self.period_type == const.REPEAT_DAY else None
        return new_task

    def delta_period_next(self):
        """
        Comparing days for create
        :return: Diff of dates
        """
        return dp.parse_iso(self.next_create) - datetime.now().date()

    def check_time(self):
        """
        Comparig of types of time to create task
        :return: True if timeto create has come
        """
        if self.time_at:
            if self.time_at['with_minutes']:
                if self.time_at['hour'] <= datetime.now().hour:
                    if self.time_at['minutes'] <= datetime.now().minute:
                        return True
            else:
                if self.time_at['hour'] <= datetime.now().hour:
                    return True
        else:
            return True

    def check_uncreated(self):
        """
        Check plans with status  create=Fasle
        :return: If all dates are food returns task
        """
        if self.check_time():
            if self.period_type == const.REPEAT_DAY:
                if self.delta_period_next() != timedelta(days=0):
                    return False
            else:
                for wday in self.period:
                    if datetime.now().weekday() != wday:
                        return False
            return self.create_task()

    def inc_next(self):
        """
        Increment of next create dates
        """
        self.next_create = (dp.parse_iso(self.last_create) + timedelta(days=int(self.period))) \
            .strftime(const.DATE_PATTERN)

    def check_created(self, tasks):
        """
        Check created plans
        :param tasks: List of tasks
        :return: function what checking dependents on type of plan
        """
        if self.period_type == const.REPEAT_DAY:
            return self.check_created_days(tasks)
        else:
            return self.check_created_wdays(tasks)

    def is_mine(self, task):
        """
        Check that task was created by this plan
        :param task: task to check
        :return: True if mine
        """
        if hasattr(task, 'plan'):
            return True if task.plan == self.id else False

    def delta_period_last(self):
        """
        checking for task created date
        :return: diff between dates
        """
        return dp.parse_iso(self.last_create) - datetime.now().date()

    def check_created_days(self, tasks):
        """
        Check created plans with type daily
        :param tasks:
        :return:
        """
        if self.delta_period_last() != timedelta(days=0):
            self.is_created = False
            for task in tasks:
                if self.is_mine(task):
                    return task

    def check_created_wdays(self, tasks):
        """
        Check created plans with type weekday
        :param tasks:
        :return:
        """
        for wday in self.period:
            if datetime.now().weekday() != wday:
                self.is_created = False
                for task in tasks:
                    if self.is_mine(task):
                        return task

    def check(self, database):
        """
        global function check
        :param database: database with all tasks
        """
        if not self.is_created:
            to_add = self.check_uncreated()
            if to_add:
                call('New task', to_add.info)
                database.add_task(to_add)
            else:
                return
        else:
            to_remove = self.check_created(database.get_tasks())
            if to_remove:
                if to_remove.status == const.STATUS_UNFINISHED:
                    call('Lost task', to_remove.info)
                    database.remove_task(to_remove.id)
