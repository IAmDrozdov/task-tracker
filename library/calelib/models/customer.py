from django.contrib.postgres.fields import ArrayField
from django.db import models


class Customer(models.Model):
    """
    Represents Customer instance.

    Fields:
        nickname(str): nickname of user
        shared_tasks(Task m2m relations): container of tasks for which this user is the performer
        tasks(Task o2m relations): container of user's tasks
        plans(Plan o2m relations): container of user's plans
        reminders(Reminder o2m relations): container of user's plans
        new_tasks(ArrayField of int): Array of task's id what had been shared and not seen
    """
    nickname = models.CharField(max_length=20, unique=True)
    shared_tasks = models.ManyToManyField('Task', related_name='performers')
    new_tasks = ArrayField(
        models.PositiveIntegerField(null=True),
        default=list
    )

    def add_task(self, task):
        """
        Add task instance to 'tasks' container

        Args:
            task(Task): Completed instance of Task
        """
        self.tasks.add(task)

    def remove_task(self, task):
        """
         Remove task instance from 'tasks' container

        Args:
            task(Task): Completed instance of Task
        """
        if self in task.performers.all():
            self.detach_task(task)
        else:
            for user in task.performers.all().iterator():
                user.detach_task(task)
            if task.parent_task:
                task.parent_task.subtasks.remove(task)
            self.tasks.remove(task)

    def add_plan(self, plan):
        """
         Add plan instance to 'plans' container

        Args:
            plan(Plan): Completed instance of Plan
        """
        self.plans.add(plan)

    def remove_plan(self, plan_id):
        """
         Remove plan instance from 'plans' container

        Args:
            plan_id(int): Primary key of plan to delete
        """
        self.plans.get(pk=plan_id).delete()

    def add_reminder(self, reminder):
        """
         Add reminder instance to 'reminders' container

        Args:
            reminder(Reminder): Completed instance of Reminder
        """
        self.reminders.add(reminder)

    def remove_reminder(self, reminder_id):
        """
         Remove reminder instance from 'reminders' container

        Args:
            reminder_id(int): Primary key of reminder to delete
        """
        self.reminders.get(pk=reminder_id).delete()

    def __str__(self):
        return self.nickname

    def apply_task(self, task):
        """
        Attach another user's task to shared_tasks
         Args:
             task: Completed instance of Task
        """
        self.new_tasks.append(task.pk)
        self.shared_tasks.add(task)
        self.save()

    def detach_task(self, task):
        """
        Detach another user's task from shared_tasks
         Args:
             task: Completed instance of Task
        """
        if task.pk in self.new_tasks:
            self.new_tasks.remove(task.pk)
        self.shared_tasks.remove(task)
        self.save()

    def clear_new_tasks(self):
        """Clear list of new tasks"""
        self.new_tasks.clear()
        self.save()
