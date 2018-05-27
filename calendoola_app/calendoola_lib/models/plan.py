import datetime as dt
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from calendoola_app.calendoola_lib.modules.logger import logg
import calendoola_app.calendoola_lib.etc.datetime_parser as dp
from calendoola_app.calendoola_lib.models.task import Task
from calendoola_app.calendoola_lib.modules.constants import Constants, Status
from calendoola_app.calendoola_lib.modules.notification import call


class Plan:
    def __init__(self, info=None, period=None, time_at=None):
        """
        Core that create tasks dependents on time
        :param info: information about task
        :param time_at: time when task should be created
        """
        self.info = info
        self.is_created = False
        self.last_create = datetime.now().strftime(Constants.DATE_PATTERN)
        self.time_at = time_at
        self.period_type = period['type']
        self.id = None
        self.period = period['period']
        if self.period_type == Constants.REPEAT_DAY:
            self.next_create = (dp.parse_iso(self.last_create) + timedelta(days=int(self.period))) \
                .strftime(Constants.DATE_PATTERN)
        elif self.period_type == Constants.REPEAT_YEAR:
            self.next_create = dt.date(datetime.now().year + 1, self.period['month'], self.period['day']) \
                .strftime(Constants.DATE_PATTERN)

    @logg('Created new Task from Plan')
    def __create_task(self):
        """
        Create new task
        :return: task object
        """
        new_task = Task(info=self.info, plan=self.id)
        self.is_created = True
        self.last_create = datetime.now().strftime(Constants.DATE_PATTERN)
        self.__inc_next_day_or_year(Constants.REPEAT_DAY) if self.period_type == Constants.REPEAT_DAY else None
        self.__inc_next_day_or_year(Constants.REPEAT_YEAR) if self.period_type == Constants.REPEAT_YEAR else None

        return new_task

    def __delta_period_next(self):
        """
        Comparing days for create
        :return: Diff of dates
        """
        return (dp.parse_iso(self.next_create) - datetime.now().date()) != timedelta(days=0)

    def __check_time(self):
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

    def __check_uncreated(self):
        """
        Check plans with status  create=Fasle
        :return: If all dates are food returns task
        """
        if self.__check_time():
            if self.period_type == Constants.REPEAT_DAY:
                if self.__delta_period_next():
                    return False
            elif self.period_type == Constants.REPEAT_WEEKDAY:
                for wday in self.period:
                    if datetime.now().weekday() != wday:
                        return False
            elif self.period_type == Constants.REPEAT_MONTH:
                if datetime.now().month not in self.period['months']:
                    if datetime.now().day != self.period['day']:
                        return False
            elif self.period_type == Constants.REPEAT_YEAR:
                if self.__delta_period_next():
                    return False
            return self.__create_task()

    def __inc_next_day_or_year(self, period_type):
        """
        Increment of next create dates
        """
        if period_type == Constants.REPEAT_DAY:
            self.next_create = (dp.parse_iso(self.last_create) + timedelta(days=int(self.period))) \
                .strftime(Constants.DATE_PATTERN)
        elif period_type == Constants.REPEAT_YEAR:
            self.next_create = (dp.parse_iso(self.last_create) + relativedelta(years=1)) \
                .strftime(Constants.DATE_PATTERN)

    def __check_created(self, tasks):
        """
        Check created plans
        :param tasks: List of tasks
        :return: function what checking dependents on type of plan
        """
        if self.period_type == Constants.REPEAT_DAY:
            return self.__check_created_days(tasks)
        elif self.period_type == Constants.REPEAT_WEEKDAY:
            return self.__check_created_wdays(tasks)
        elif self.period_type == Constants.REPEAT_MONTH:
            return self.__check_created_months(tasks)
        elif self.period_type == Constants.REPEAT_YEAR:
            return self.__check_created_year(tasks)

    def __is_mine(self, task):
        """
        Check that task was created by this plan
        :param task: task to check
        :return: True if mine
        """
        if hasattr(task, 'plan'):
            return True if task.plan == self.id else False

    def __delta_period_last(self):
        """
        checking for task created date
        :return: diff between dates
        """
        return dp.parse_iso(self.last_create) - datetime.now().date()

    def __check_created_days(self, tasks):
        """
        Check created plans with type "day"
        :param tasks:list of tasks to check
        :return:
        """
        if self.__delta_period_last():
            self.is_created = False
            for task in tasks:
                if self.__is_mine(task):
                    return task

    def __check_created_months(self, tasks):
        """
        Check created tasks with type "month"
        :param tasks: list of tasks to check
        :return: returns task if its should be removed
        """
        if datetime.now().month not in self.period['months']:
            self.is_created = False
            for task in tasks:
                if self.__is_mine(task):
                    return task
        pass

    def __check_created_year(self, tasks):
        """
        Check tasks with type "year"
        :param tasks: list of tasks to check
        :return: returns task if its should be removed
        """
        if self.__delta_period_last():
            self.is_created = False
            for task in tasks:
                if self.__is_mine(task):
                    return task

    def __check_created_wdays(self, tasks):
        """
        Check created plans with type "weekday"
        :param tasks: list of tasks to check
        :return:
        """
        if datetime.now().weekday() not in self.period:
            self.is_created = False
            for task in tasks:
                if self.__is_mine(task):
                    return task

    @logg('Checking Plans')
    def check(self, database):
        """
        global function check
        :param database: database with all tasks
        """
        if not self.is_created:
            to_add = self.__check_uncreated()
            if to_add:
                call('New task', to_add.info)
                database.add_task(to_add)
            else:
                return
        else:
            to_remove = self.__check_created(database.get_tasks())
            if to_remove:
                if to_remove.status == Status.UNFINISHED:
                    call('Lost task', to_remove.info)
                    database.remove_task(to_remove.id)
