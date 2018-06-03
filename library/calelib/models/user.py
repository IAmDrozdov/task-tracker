import django.core.exceptions
from calelib.logger import logg
from django.db import models


class User(models.Model):
    nickname = models.CharField(max_length=20, unique=True)
    tasks = models.ManyToManyField('Task')
    plans = models.ManyToManyField('Plan', symmetrical=False)
    reminders = models.ManyToManyField('Reminder', symmetrical=False)

    @logg('Added task to user')
    def add_task(self, task):
        self.tasks.add(task)
        self.save()

    @logg('Removed task from user')
    def remove_task(self, task_id):
        self.search_task(task_id).delete()

    @logg('Added plan to user')
    def add_plan(self, plan):
        self.plans.add(plan)
        self.save()

    @logg('Removed plan from user')
    def remove_plan(self, plan_id):
        self.plans.get(pk=plan_id).delete()
        self.save()

    def search_task(self, task_id):
        def search_in_subtasks(subtasks):
            if subtasks.exists():
                for task in subtasks.all():
                    if task.subtasks.filter(pk=task_id).exists():
                        return task.subtasks.get(pk=task_id)
                    else:
                        return search_in_subtasks(task.subtasks)

        if self.tasks.filter(pk=task_id).exists():
            return self.tasks.get(pk=task_id)
        else:
            found_task = search_in_subtasks(self.tasks)
            if found_task:
                return found_task
            else:
                raise django.core.exceptions.ObjectDoesNotExist

    @logg('Created new reminder')
    def add_reminder(self, reminder):
        self.reminders.add(reminder)
        self.save()

    @logg('Removed reminder')
    def remove_reminder(self, reminder_id):
        self.reminders.get(pk=reminder_id).delete()
        self.save()
