import operator
from functools import reduce

from calelib.config import Config
from calelib.logger import (
    configure_logger,
    logg,
)
from calelib.models import (
    Customer,
    Plan,
    Reminder,
    Task
)
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    F,
    Q,
)


class Calendoola:
    """Represents Calendoola application instants"""

    def __init__(self):
        self.cfg = Config()
        log_path = self.cfg.get_field('logging_path')
        log_level = self.cfg.get_field('logging_level')
        log_format = self.cfg.get_field('logging_format')
        configure_logger(log_path, log_format, log_level)

    @logg('Removed task')
    def remove_task(self, username, task_id):
        """
        Remove task from user's tasks container
        Args:
            username(str): nickname of user where will delete
            task_id(int): ID of task to delete
        """
        user = self.get_users(username)
        task = self.get_tasks(username, task_id)
        user.remove_task(task)

    @logg('Created new task')
    def create_task(self, username, info, priority=1, deadline=None, tags=None, parent_task_id=None):
        """
        Create task to user's task container
        Args:
            username(str): nickname of user where to add task
            info(str): description of task
            parent_task_id(Tint): ID of task in which subtasks container this task in
            tags(str): tags for task
            priority(int): importance of task(1..5)
            deadline(datetime): date when task will be overdue
        """
        task = Task(info=info, priority=priority, deadline=deadline, tags=tags)
        user = self.get_users(username)
        if parent_task_id:
            parent_task = user.tasks.get(pk=parent_task_id)
            task.save()
            parent_task.add_subtask(task)
        else:
            task.save()
        user.add_task(task)

    def get_tasks(self, username, task_id=None, tags=None, archive=False, info=None, primary=True):
        """
        Return set of tasks of user
        Args:
            username(str): user which tasks will be returned
            task_id(int): ID of task to return. If not founr raises ObjectNotExists 
            tags(str): filter tasks by tags
            archive(bool): if True returns archived tasks
            info(str): filter tasks by info
            primary(bool): return tasks without parents
        """
        user = self.get_users(username)
        if tags:
            query = user.tasks.filter(reduce(operator.and_, (Q(tags__contains=tag) for tag in tags)))
        elif info:
            query = user.tasks.filter(info__contains=info)
        elif task_id:
            try:
                return user.tasks.get(pk=task_id)
            except ObjectDoesNotExist:
                return user.shared_tasks.get(pk=task_id)

        elif archive:
            query = user.tasks.filter(archived=True)
        else:
            return user.tasks.filter(archived=False).filter(parent_task__isnull=True) \
                   | user.shared_tasks.filter(archived=False)
        return query.filter(parent_task__isnull=True) if primary else query

    @logg('CHanged task')
    def change_task(self, username, task_id, info=None, deadline=None, priority=None, status=None,
                    plus_tags=None, minus_tags=None):
        """
        Change users task
        Args:
            username(str): user what task will be updated
            task_id(int): ID of task to update
            info(str): new description
            deadline(datetime): new deadline
            priority(int: new priority
            status(str): new status
            plus_tags(str): add tags
            minus_tags(str): remive tags
        """
        self.get_tasks(username, task_id).update(info, deadline, priority, status, plus_tags, minus_tags)

    def get_plans(self, username, plan_id=None):
        """
        Return user's plans
        Args:
            username(str): user whick plans will be returned 
            plan_id(int): ID of plan to return 
        """
        user = self.get_users(username)
        return user.plans.get(pk=plan_id) if plan_id else user.plans.all()

    @logg('Created plan')
    def create_plan(self, username, info, period_value, period_type, time_at=None):
        """
        Create new plan to users plans
        Args:
            username(str): nickname of user  
            info(str): description of task what will be created 
            period_type(str): 
                'd', day: create task after every N days
                'wd' week: create task every given weekdays
                'm', month: create task every given day at given months
            period_value(dict):
                dependents on period type:
                 'd'-period = {'day':int day period number}
                'wd'-period = {'days':list of int weekdays}
                'm'-period = {'months': list of int months, 'day': int day of month}
            time_at(datetime.time): time when plan should create task
        """
        user = self.get_users(username)
        plan = Plan(info=info, period=period_value, period_type=period_type, time_at=time_at)
        plan.save()
        user.add_plan(plan)

    @logg('Removed plan')
    def remove_plan(self, username, plan_id):
        """
        Remove plan from users plans container
        Args:
            username(str): nickname of user 
            plan_id(int): ID of plan to delete 
        """
        user = self.get_users(username)
        user.remove_plan(plan_id)

    @logg('Changed plan')
    def change_plan(self, username, plan_id, info=None, period_type=None, period_value=None, time=None):
        """
        Change information about user's plan
        Args: 
            username(str): nickname of user
            plan_id(int): ID of plan to update 
            info(str): new info 
            period_type(str): new type 
            period_value(dict): ne value 
            time(datetime.time): new time 
        """
        user = self.get_users(username)
        user.plans.get(pk=plan_id).update(info, period_type, period_value, time)

    @staticmethod
    @logg('Created new user')
    def create_user(username):
        """
        Create new user
        Args:
            username: new user's nickname 
        """
        Customer.objects.create(nickname=username)

    @staticmethod
    @logg('Removed user')
    def remove_user(username):
        """
        Remove user. 
        Args:
            username: user's nickname to delete 
        """
        Customer.objects.get(nickname=username).delete()

    @staticmethod
    def get_users(username=None):
        """
        Return user or set of users
            username: nickname of user to return. if not exist create new   
        """
        if username:
            return Customer.objects.get_or_create(nickname=username)[0]
        else:
            return Customer.objects.all()

    @logg('Created new reminder to user')
    def create_reminder(self, username, remind_type, remind_before):
        """
        Create new reminder to users reminders container
        Args:
            username(str): nickname of user
            remind_before(int): value what converts in remind_type measure
            remind_type(str):
                'm', minutes: remind before minutes
                'h', hours: remind before hours
                'd', days: remind before days
                'mth', months: remind before months
        """
        user = self.get_users(username)
        reminder = Reminder(remind_type=remind_type, remind_before=remind_before)
        reminder.save()
        user.add_reminder(reminder)

    @logg('Removed reminder from user')
    def remove_reminder(self, username, reminder_id):
        """
        Remove reminder from user
        Args:
            username: nickname of user
            reminder_id(int): ID of reminder to delete
        :return:
        """
        user = self.get_users(username)
        user.remove_reminder(reminder_id)

    def get_reminders(self, username, reminder_id=None):
        """
        Return user's reminder of set of reminders
        Args:
            username(str): nickname of user
            reminder_id(int): ID of reminder to return
        :return:
        """
        user = self.get_users(username)
        return user.reminders.get(pk=reminder_id) if reminder_id else user.reminders.all()

    @logg('Changed reminder')
    def change_reminder(self, username, reminder_id, remind_type=None, remind_value=None):
        """
        Change information about user's reminder
        Args:
            username(str): nickname of user
            reminder_id(int): ID of reminder to update
            remind_type(str); new reminder type
            remind_value(int): new reminder_before value
        """
        user = self.get_users(username)
        user.reminders.get(pk=reminder_id).update(remind_type, remind_value)

    @logg('Added completed object of class')
    def add_completed(self, username, klass, instance):
        """
        Add new completed instance in dependent of klass user's container
        Args:
            username(str): nickname of user
            klass(str):
                'reminder'
                'task'
                'plan'
            instance(Plan, Task, Reminder: completed object
        """
        user = self.get_users(username)
        if klass == 'task':
            user.add_task(instance)
        elif klass == 'plan':
            user.add_plan(instance)
        elif klass == 'reminder':
            user.add_reminder(instance)
        else:
            raise AttributeError

    def get_sorted_tasks(self, username, field, vector, primary=True):
        """
        Get sorted set of user's task
        Args:
            username(str): nickname of user
            field(str): task's field to sort
            vector:
                'desc'
                'asc'
            primary: if True return only tasks without parent
        """
        query = self.get_tasks(username, primary=primary)
        if vector == 'desc':
            return query.order_by(F(field).desc(nulls_last=True))
        else:
            return query.order_by(F(field).asc())
