import operator
from functools import reduce

from calelib.config import Config
from calelib.constants import Constants
from calelib.logger import logg, configure_logger
from calelib.models import Customer, Task, Plan, Reminder
from django.db.models import F
from django.db.models import Q


class Calendoola:
    def __init__(self, ):
        self.cfg = Config(Constants.CONFIG_FILE_PATH)
        log_path = self.cfg.get_config_field('logging_path')
        log_level = self.cfg.get_config_field('logging_level')
        log_format = self.cfg.get_config_field('logging_format')
        configure_logger(log_path, log_format, log_level)

    @logg('Removed task')
    def remove_task(self, username, task_id):
        user = self.get_users(username)
        user.remove_task(task_id)

    @logg('Created new task')
    def create_task(self, username, info=None, priority=None, deadline=None, tags=None, parent_task_id=None):
        task = Task(info=info, priority=priority, deadline=deadline, tags=tags)
        user = self.get_users(username)
        if parent_task_id:
            parent_task = user.tasks.get(pk=parent_task_id)
            task.save()
            parent_task.add_subtask(task)
        else:
            task.save()
        user.add_task(task)

    def get_tasks(self, username, task_id=None, tags=None, archive=False, info=None):
        user = self.get_users(username)
        if tags:
            return user.tasks.filter(reduce(operator.and_, (Q(tags__contains=tag) for tag in tags)))
        elif info:
            return user.tasks.filter(info__contains=info)
        elif task_id:
            return user.search_task(task_id)
        elif archive:
            return user.tasks.filter(archived=True)
        else:
            return user.tasks.filter(archived=False)

    @logg('CHanged task')
    def change_task(self, username, task_id, info, deadline, priority, status, plus_tags, minus_tags):
        user = self.get_users(username)
        user.search_task(task_id).update(info, deadline, priority, status, plus_tags, minus_tags)

    def get_plans(self, username, plan_id=None):
        user = self.get_users(username)
        return user.plans.get(pk=plan_id) if plan_id else user.plans.all()

    @logg('Created plan')
    def create_plan(self, username, info, period_value, period_type, time_at):
        user = self.get_users(username)
        plan = Plan(info=info, period=period_value, period_type=period_type, time_at=time_at)
        plan.save()
        user.add_plan(plan)

    @logg('Removed plan')
    def remove_plan(self, username, plan_id):
        user = self.get_users(username)
        user.remove_plan(plan_id)

    @logg('Changed plan')
    def change_plan(self, username, plan_id, info, period_type, period_value, time):
        user = self.get_users(username)
        user.plans.get(pk=plan_id).update(info, period_type, period_value, time)

    @staticmethod
    @logg('Created new user')
    def create_user(username):
        Customer.objects.create(nickname=username)

    @staticmethod
    @logg('Removed user')
    def remove_user(username):
        Customer.objects.get(nickname=username).delete()

    @staticmethod
    def get_users(username=None):
        if username:
            try:
                user = Customer.objects.get(nickname=username)
                return user
            except Customer.DoesNotExist:
                user = Customer(nickname=username)
                user.save()
                return user
        else:
            return Customer.objects.all()

    @logg('Created new reminder to user')
    def create_reminder(self, username, remind_type, remind_before):
        user = self.get_users(username)
        reminder = Reminder(remind_type=remind_type, remind_before=remind_before)
        reminder.save()
        user.add_reminder(reminder)

    @logg('Removed reminder from user')
    def remove_reminder(self, username, reminder_id):
        user = self.get_users(username)
        user.remove_reminder(reminder_id)

    def get_reminders(self, username, reminder_id=None):
        user = self.get_users(username)
        return user.reminders.get(pk=reminder_id) if reminder_id else user.reminders.all()

    @logg('Changed reminder')
    def change_reminder(self, username, reminder_id, remind_type, remind_value):
        user = self.get_users(username)
        user.reminders.get(pk=reminder_id).update(remind_type, remind_value)

    @logg('Added completed object of class')
    def add_completed(self, username, klass, instance):
        user = self.get_users(username)
        if klass == 'task':
            user.add_task(instance)
        elif klass == 'plan':
            user.add_plan(instance)
        elif klass == 'reminder':
            user.add_reminder(instance)
        else:
            raise AttributeError

    def get_sorted_tasks(self, username, field, type):
        if type == 'desc':
            return self.get_users(username).tasks.order_by(F(field).desc(nulls_last=True))
        else:
            return self.get_users(username).tasks.order_by(F(field).asc())

    def get_all_tasks(self, username):
        user = self.get_users(username)
        task_array = []

        def rec_down(tasks):
            for task in tasks:
                task_array.append(task)
                rec_down(task.subtasks.all())

        rec_down(self.get_tasks(user))
        return Task.objects.filter(pk__in=[t.pk for t in task_array])
