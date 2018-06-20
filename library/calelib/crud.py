import operator
from functools import reduce

from calelib.config import Config
from calelib.logger import configure_logger, logg
from calelib.models import Customer, Plan, Reminder, Task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q


class Calendoola:
    def __init__(self, ):
        self.cfg = Config()
        log_path = self.cfg.get_field('logging_path')
        log_level = self.cfg.get_field('logging_level')
        log_format = self.cfg.get_field('logging_format')
        configure_logger(log_path, log_format, log_level)

    @logg('Removed task')
    def remove_task(self, username, task_id):
        user = self.get_users(username)
        task = self.get_tasks(username, task_id)
        user.remove_task(task)

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

    def get_tasks(self, username, task_id=None, tags=None, archive=False, info=None, primary=True):
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
            return Customer.objects.get_or_create(nickname=username)[0]
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

    def get_sorted_tasks(self, username, field, vector, primary=True):
        query = self.get_tasks(username, primary=primary)
        if vector == 'desc':
            return query.order_by(F(field).desc(nulls_last=True))
        else:
            return query.order_by(F(field).asc())
