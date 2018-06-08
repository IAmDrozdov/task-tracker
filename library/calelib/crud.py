from calelib.config import Config
from calelib.constants import Constants
from calelib.logger import logg, configure_logger
from calelib.models import User, Task, Plan, Reminder
from django.core.exceptions import ObjectDoesNotExist

class Calendoola:
    def __init__(self, ):

        self.cfg = Config(Constants.CONFIG_FILE_PATH)
        log_path = self.cfg.get_config_field('logging_path')
        log_level = self.cfg.get_config_field('logging_level')
        log_format = self.cfg.get_config_field('logging_format')
        try:
            self._current_user = User.objects.get(nickname='guess')
        except ObjectDoesNotExist:
            User.objects.create(nickname='guess')
            self._current_user = User.objects.get(nickname='guess')
        configure_logger(log_path, log_format, log_level)

    @property
    def current_user(self):
        return self._current_user

    @current_user.setter
    def current_user(self, nickname):
        self._current_user = User.objects.get(nickname=nickname)

    @current_user.deleter
    def current_user(self):
        self.cfg.set_current_user('guess')

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
    def create_task(self, info, priority, deadline, tags, parent_task_id):
        task = Task(info=info, priority=priority, deadline=deadline, tags=tags)
        if parent_task_id:
            parent_task = self._current_user.tasks.get(pk=parent_task_id)
            task.save()
            parent_task.add_subtask(task)
        else:
            task.save()
        self._current_user.add_task(task)

    @logg('CHanged task')
    def change_task(self, task_id, info, deadline, priority, status, plus_tags, minus_tags):
        self._current_user.search_task(task_id).update(info, deadline, priority, status, plus_tags, minus_tags)

    def get_plans(self, plan_id=None):
        return self._current_user.plans.get(pk=plan_id) if plan_id else self._current_user.plans.all()

    @logg('Created plan')
    def create_plan(self, info, period_value, period_type, time_at):
        plan = Plan(info=info, period=period_value, period_type=period_type, time_at=time_at)
        plan.save()
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
    def get_users(user_nickname=None):
        return User.objects.get(nickname=user_nickname) if user_nickname else User.objects.all()

    @logg('Created new reminder to user')
    def create_reminder(self, remind_type, remind_before):
        reminder = Reminder(remind_type=remind_type, remind_before=remind_before)
        reminder.save()
        self._current_user.add_reminder(reminder)

    @logg('Removed reminder from user')
    def remove_reminder(self, reminder_id):
        self._current_user.remove_reminder(reminder_id)

    def get_reminders(self, reminder_id=None):
        return self._current_user.reminders.get(pk=reminder_id) if reminder_id else self._current_user.reminders.all()

    @logg('Changed reminder')
    def change_reminder(self, reminder_id, remind_type, remind_value):
        self._current_user.reminders.get(pk=reminder_id).update(remind_type, remind_value)
