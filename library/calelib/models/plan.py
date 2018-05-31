import datetime

from calelib.constants import Constants
from calelib.logger import logg
from calelib.models.task import Task
from dateutil.relativedelta import relativedelta
from django.contrib.postgres.fields import HStoreField
from django.db import models


class Plan(models.Model):
    """
    'd'-period = {'day':int day period number}
    'wd'-period = {'days':list of int weekdays}
    'm'-period = {'months': list of int months, 'day': int day of month}
    'y'-period = {'day': int month day, 'month': int month number}
    """
    info = models.CharField(max_length=100)
    created = models.BooleanField(default=False)
    last_create = models.DateField(auto_now=True)
    time_at = HStoreField(null=True)
    period_type = models.CharField(max_length=6,
                                   choices=[
                                       (Constants.REPEAT_DAY, 'day'),
                                       (Constants.REPEAT_WEEKDAY, 'week'),
                                       (Constants.REPEAT_MONTH, 'month'),
                                       (Constants.REPEAT_YEAR, 'year')
                                   ]
                                   )

    period = HStoreField(null=True)

    @logg('Created planned task')
    def create_task(self):
        new_task = Task(info=self.info, plan=self.pk)
        new_task.save()
        self.created = True
        self.last_create = datetime.datetime.now().date()
        return new_task

    @logg('Removed planned task')
    def remove_task(self):
        self.created = False
        Task.objects.get(plan=self.pk)

    def check_last_create_day(self):
        return self.last_create + relativedelta(days=self.period) != datetime.datetime.now().date()

    def check_last_create_year(self):
        now = datetime.datetime.now()
        return self.period['day'] != now.day and self.period['month'] != now.month

    def check_time(self):
        now = datetime.datetime.now()
        if self.time_at:
            if self.time_at['with_minutes']:
                if self.time_at['hour'] <= now.hour:
                    if self.time_at['minutes'] <= now.minute:
                        return True
            else:
                if self.time_at['hour'] <= now.hour:
                    return True
        else:
            return True

    def check_uncreated(self):
        if self.check_time():
            now = datetime.datetime.now()
            if self.period_type == Constants.REPEAT_DAY:
                if self.check_last_create_day():
                    return False
            elif self.period_type == Constants.REPEAT_WEEKDAY:
                if now.weekday() not in self.period['days']:
                    return False
            elif self.period_type == Constants.REPEAT_MONTH:
                if now.month not in self.period['months'] or now.day != self.period['day']:
                    return False
            elif self.period_type == Constants.REPEAT_YEAR:
                if self.check_last_create_year():
                    return False
            return self.create_task()

    def check_created_days(self):
        if self.last_create - datetime.datetime.now().date():
            self.remove_task()

    def check_created_wdays(self):
        if datetime.datetime.now().weekday() not in self.period['days']:
            self.remove_task()

    def check_created_months(self):
        if datetime.datetime.now().month not in self.period['months']:
            self.remove_task()

    def check_created_year(self):
        if self.last_create - datetime.datetime.now().date():
            self.remove_task()

    def check_created(self):
        if self.period_type == Constants.REPEAT_DAY:
            return self.check_created_days()
        elif self.period_type == Constants.REPEAT_WEEKDAY:
            return self.check_created_wdays()
        elif self.period_type == Constants.REPEAT_MONTH:
            return self.check_created_months()
        elif self.period_type == Constants.REPEAT_YEAR:
            return self.check_created_year()

    @logg('Checked plan')
    def check_for_create(self):
        if self.created:
            self.check_created()
        else:
            return self.check_uncreated()
