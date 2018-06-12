import django.core.exceptions
from django.db import models


class User(models.Model):
    nickname = models.CharField(max_length=20, unique=True)
    tasks = models.ManyToManyField('Task')
    plans = models.ManyToManyField('Plan', symmetrical=False)
    reminders = models.ManyToManyField('Reminder', symmetrical=False)

    def add_task(self, task):
        self.tasks.add(task)
        self.save()

    def remove_task(self, task_id):
        self.search_task(task_id).delete()

    def add_plan(self, plan):
        self.plans.add(plan)
        self.save()

    def remove_plan(self, plan_id):
        self.plans.get(pk=plan_id).delete()
        self.save()

    def search_task(self, task_id):
        def search_in_subtasks(subtasks):
            if subtasks.exists():
                for task in subtasks:
                    if task.subtasks.filter(pk=task_id).exists():
                        return task.subtasks.get(pk=task_id)
                    else:
                        return search_in_subtasks(task.subtasks.all())

        if self.tasks.filter(pk=task_id).exists():
            return self.tasks.get(pk=task_id)
        else:
            found_task = search_in_subtasks(self.tasks.all())
            if found_task:
                return found_task
            else:
                raise django.core.exceptions.ObjectDoesNotExist

    def add_reminder(self, reminder):
        self.reminders.add(reminder)
        self.save()

    def remove_reminder(self, reminder_id):
        self.reminders.get(pk=reminder_id).delete()
        self.save()

    def __str__(self):
        return self.nickname