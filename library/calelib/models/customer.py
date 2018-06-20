from django.db import models


class Customer(models.Model):
    nickname = models.CharField(max_length=20, unique=True)
    shared_tasks = models.ManyToManyField('Task', related_name='performers')

    def add_task(self, task):
        self.tasks.add(task)

    def remove_task(self, task):
        if self in task.performers.all():
            self.detach_task(task)
        else:
            for user in task.performers.all().iterator():
                user.detach_task(task)
            self.tasks.remove(task)

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

    def apply_task(self, task):
        self.shared_tasks.add(task)

    def detach_task(self, task):
        self.shared_tasks.remove(task)
