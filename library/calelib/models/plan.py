import json

from calelib.constants import (
    Constants,
    Notifications,
)
from calelib.logger import logg
from calelib.models.task import Task
from calelib.notification import Notification
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """
    'd'-period = {'day':int day period number}
    'wd'-period = {'days':list of int weekdays}
    'm'-period = {'months': list of int months, 'day': int day of month}
    'y'-period = {'day': int month day, 'month': int month number}
    """
    """
    Represents Plan instance
    Fields:
        info(str): description for task what will be created
        owner(Customer): Customer instance which created this plan
        created(bool): field which shows created this plan task or not
        last_create(datetime): last creation
        time_at(datetime.time): time when plan should create task
        period_type(str): 
            'd', day: create task after every N days
            'wd' week: create task every given weekdays
            'm', month: create task every given day at given months
        able: field which shows should plan create or not
        _period(dict):
            dependents on period type:
             'd'-period = {'day':int day period number}
            'wd'-period = {'days':list of int weekdays}
            'm'-period = {'months': list of int months, 'day': int day of month}
    """

    info = models.CharField(max_length=100)
    owner = models.ForeignKey(
        'Customer',
        related_name='plans',
        null=True,
        on_delete=models.CASCADE,
    )
    created = models.BooleanField(default=False)
    last_create = models.DateTimeField(auto_now=True)
    time_at = models.TimeField(null=True, blank=True)
    period_type = models.CharField(max_length=6,
                                   choices=[
                                       (Constants.REPEAT_DAY, 'day'),
                                       (Constants.REPEAT_WEEKDAY, 'week'),
                                       (Constants.REPEAT_MONTH, 'month'), ])
    able = models.BooleanField(default=True)
    _period = JSONField(
        db_column='period',
        default=dict
    )

    @property
    def period(self):
        """Returns readable for python data"""
        return json.loads(self._period)

    @period.setter
    def period(self, not_dumped_period):
        """Dumps new data"""
        self._period = json.dumps(not_dumped_period)
        self.save()

    @logg('Created planned task')
    def create_task(self):
        """
        Creates new periodic tasks if its time has come
        Return:
            tuple of new task object and notification
        """
        new_task = Task(info=self.info, plan=self)
        new_task.save()
        self.created = True
        self.last_create = timezone.localtime().date()
        self.save()
        return new_task, Notification(
            title=Notifications.PLANNED,
            info=self.info
        )

    @logg('Removed planned task')
    def remove_task(self):
        """
        Removes task if plan overdue
        Return:
            tuple of string with notification status and notification
        """
        self.created = False
        self.save()
        Task.objects.get(plan=self).delete()
        return Notifications.REMOVED, Notification(
            title=Notifications.REMOVED,
            info=self.info
        )

    def check_last_create_day(self):
        """Comparing now date and date, when last plan created"""
        return self.last_create + timezone.timedelta(days=int(self.period['day'])) != timezone.localtime().date()

    def check_time(self):
        """Comparing time for creating. If plan has no time_at, returns True"""
        now = timezone.localtime()
        if self.time_at:
            if self.time_at <= now.time():
                return True
        else:
            return True

    def check_uncreated(self):
        """Selecting uncreated plan for period types"""
        if self.check_time():
            now = timezone.localtime()
            if self.period_type == Constants.REPEAT_DAY:
                if self.check_last_create_day():
                    return None, None
            elif self.period_type == Constants.REPEAT_WEEKDAY:
                if now.weekday() not in self.period['days']:
                    return None, None
            elif self.period_type == Constants.REPEAT_MONTH:
                if now.month not in self.period['months'] or now.day != self.period['day']:
                    return None, None
            return self.create_task()

    def check_created_days(self):
        """Check created plans with type 'd' for deleting task"""
        if self.last_create.date() - timezone.localtime().date():
            return self.remove_task()
        else:
            return None, None

    def check_created_wdays(self):
        """Check created plans with type 'wd' for deleting task"""

        if timezone.localtime().weekday() not in self.period['days']:
            return self.remove_task()
        else:
            return None, None

    def check_created_months(self):
        """Check created plans with type 'm' for deleting task"""

        if timezone.localtime().month not in self.period['months']:
            return self.remove_task()
        else:
            return None, None

    def check_created(self):
        """Selecting created plan for period types"""
        if self.period_type == Constants.REPEAT_DAY:
            return self.check_created_days()
        elif self.period_type == Constants.REPEAT_WEEKDAY:
            return self.check_created_wdays()
        elif self.period_type == Constants.REPEAT_MONTH:
            return self.check_created_months()

    @logg('Checked plan')
    def check_for_create(self):
        """Method to check self for being deleted or creating"""
        if self.able:
            if self.created:
                return self.check_created()
            else:
                return self.check_uncreated()

    @logg('Changed plan state')
    def set_state(self):
        """Set state able<->not able"""
        self.able = not self.able
        self.save()

    @logg('Chaned information about plan')
    def update(self, info=None, period_type=None, period_value=None, time=None):
        """Updates information about plan"""
        if info:
            self.info = info
        if time:
            self.time_at = time
        if period_type:
            self.period = period_value
            self.period_type = period_type
        self.save()

    def __str__(self):
        return '{} {} {}'.format(self.info, self.period_type, self.period)
