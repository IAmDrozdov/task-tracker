from copy import deepcopy
from datetime import datetime

from calelib.constants import Status
from calelib.custom_exceptions import CycleError
from calelib.logger import logg
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Task(models.Model):
    info = models.CharField(max_length=100)
    subtasks = models.ManyToManyField('self', symmetrical=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = ArrayField(models.CharField(max_length=20), default=list)
    priority = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], default=1)
    deadline = models.DateTimeField(null=True, blank=True)  # 'YYYY-MM-DD'
    status = models.CharField(max_length=10, default=Status.UNFINISHED)
    plan = models.ForeignKey('Plan', null=True)

    @logg('Added subtask')
    def add_subtask(self, task):
        self.subtasks.add(task)
        self.save()

    @logg('Copied task')
    def get_copy(self):
        copied = deepcopy(self)
        copied.id = None
        copied.save()
        return copied

    @logg('Finished task')
    def finish(self):
        self.status = Status.FINISHED
        for task in self.subtasks.all():
            task.finish()

    @logg('Unfinished taks')
    def unfinish(self):
        self.status = Status.UNFINISHED
        for task in self.subtasks.all():
            task.finish()

    @logg('Changed information about task')
    def update(self, info=None, deadline=None, priority=None, status=None, plus_tag=None, minus_tag=None):
        if info:
            self.info = info
        if deadline:
            self.deadline = deadline
        if priority:
            self.priority = priority
        if status == Status.FINISHED:
            self.finish()
        elif status:
            self.status = status
        if plus_tag:
            self.tags.extend(plus_tag)
        if minus_tag:
            self.tags = [tag for tag in self.tags if tag not in minus_tag]
        self.save()

    def __rec_up(self, id):
        for task in self.subtasks.all():
            if task.id == id:
                return True
            else:
                task.__rec_up(id)

    @logg('Task checked for cycles')
    def is_parent(self, id):
        if self.__rec_up(id):
            raise CycleError
        else:
            return False

    @logg('''Checked task's deadline''')
    def check_deadline(self):
        if self.deadline is not None:
            if self.deadline.date() < datetime.now().date() and self.status == Status.UNFINISHED:
                self.status = Status.OVERDUE
                return self
