from calelib.models import User
import logging
from calelib.logger import logg


def configure_logger(path, log_format, level):
    clogger = logging.getLogger('calendoola_logger')
    handler = logging.FileHandler(path)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    clogger.addHandler(handler)
    clogger.setLevel(getattr(logging, level))


class Calendoola:
    def __init__(self, log_path, log_format, log_level):
        self._current_user = None
        configure_logger(log_path, log_format, log_level)
    current_user = property()

    @current_user.setter
    def current_user(self, nickname):
        self._current_user = User.objects.get(nickname=nickname)

    @current_user.getter
    def current_user(self):
        return self._current_user

    @current_user.deleter
    def current_user(self):
        self._current_user = None

    def get_tasks(self, task_id=None, tags=None, archive=False):
        if tags:
            return self._current_user.tasks.filter(tags__contains=tags)
        elif task_id:
            return self._current_user.search_task(task_id)
        elif archive:
            return self._current_user.tasks.filter(archived=True)
        else:
            return self._current_user.tasks.filter(archived=False)

    @logg('Removed task')
    def remove_task(self, task_id):
        self._current_user.remove_task(task_id)

    @logg('Created new task')
    def create_task(self, task):
        self._current_user.add_task(task)

    @logg('CHanged task')
    def change_task(self, task_id, info, deadline, priority, status, plus_tags, minus_tags):
        self._current_user.search_task(task_id).update(info, deadline, priority, status, plus_tags, minus_tags)

    def get_plans(self, plan_id=None):
        return self._current_user.plans.get(pk=plan_id) if plan_id else self._current_user.plans.all()

    @logg('Created plan')
    def create_plan(self, plan):
        self._current_user.add_plan(plan)

    @logg('Removed plan')
    def remove_plan(self, plan_id):
        self._current_user.remove_plan(plan_id)

    @logg('Changed plan')
    def change_plan(self, plan_id, info, period_type, period_value, time):
        self._current_user.plans.get(pk=plan_id).update(info, period_type, period_value, time)

    @staticmethod
    @logg('Created new user')
    def create_user(nickname):
        User.objects.create(nickname=nickname)

    @staticmethod
    @logg('Removed user')
    def remove_user(nickname):
        User.objects.get(nickname=nickname).delete()

    @staticmethod
    def get_users(user_nickname):
        return User.objects.get(nickname=user_nickname) if user_nickname else User.objects.all()

    @logg('Created new reminder to user')
    def create_reminder(self, reminder):
        self._current_user.add_reminder(reminder)

    @logg('Removed reminder from user')
    def remove_reminder(self, reminder_id):
        self._current_user.remove_reminder(reminder_id)

    def get_reminders(self, reminder_id=None):
        return self._current_user.reminders.get(pk=reminder_id) if reminder_id else self._current_user.reminders.all()

    @logg('Changed reminder')
    def change_reminder(self, reminder_id, remind_type, remind_value):
        self._current_user.reminders.get(pk=reminder_id).update(remind_type, remind_value)
