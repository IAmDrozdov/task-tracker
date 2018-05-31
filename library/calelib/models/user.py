from calelib.logger import logg
from django.db import models


class User(models.Model):
    nickname = models.CharField(max_length=20, unique=True)
    tasks = models.ManyToManyField('Task', related_name='active_tasks')
    plans = models.ManyToManyField('Plan')
    archive = models.ManyToManyField('Task', related_name='archived_tasks')

    @logg('Added task to user')
    def add_task(self, task):
        self.tasks.add(task)
        self.save()

    @logg('Removed task from user')
    def remove_task(self, task_id):
        self.tasks.filter(pk=task_id).delete()

    @logg('Added plan to user')
    def add_plan(self, plan):
        self.plans.add(plan)
        self.save()

    @logg('Removed plan from user')
    def remove_plan(self, plan_id):
        self.plans.filter(pk=plan_id).delete()
        self.save()

    @logg('Archived task')
    def archive_task(self, task_id):
        task = self.tasks.get(pk=task_id)
        self.archive.add(task.get_copy())
        self.tasks.filter(pk=task_id).delete()
        self.save()
