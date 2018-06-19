import django.core.exceptions
from django.db import models


class Customer(models.Model):
    nickname = models.CharField(max_length=20, unique=True)

    def add_task(self, task):
        self.tasks.add(task)

    def remove_task(self, task_id):
        self.tasks.filter(task_id).delete()

    def add_plan(self, plan):
        self.plans.add(plan)

    def remove_plan(self, plan_id):
        self.plans.get(pk=plan_id).delete()

    def add_reminder(self, reminder):
        self.reminders.add(reminder)

    def remove_reminder(self, reminder_id):
        self.reminders.get(pk=reminder_id).delete()

    def __str__(self):
        return self.nickname
