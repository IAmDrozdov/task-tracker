from copy import deepcopy
from datetime import datetime

from calelib.constants import Status
from calelib.custom_exceptions import CycleError
from calelib.logger import logg
from calelib.notification import call
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Task(models.Model):
    PRIORITIES = ((num + 1, num + 1) for num in range(5))

    owner = models.ForeignKey(
        'Customer',
        null=True,
        on_delete=models.CASCADE,
        related_name='tasks',
        related_query_name='task'
    )
    info = models.CharField(
        max_length=100,
        help_text='Enter what to do')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subtasks',
        null=True
    )
    tags = models.CharField(
        null=True,
        blank=True,
        max_length=20,
        help_text='Some grouping info'
    )
    priority = models.PositiveSmallIntegerField(
        choices=PRIORITIES,
        default=1,
        help_text='Need for speed'
    )
    status = models.CharField(
        max_length=15,
        default=Status.UNFINISHED
    )
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        help_text='When you will lose task'
    )
    plan = models.ForeignKey(
        'Plan',
        null=True,
        on_delete=models.CASCADE
    )
    archived = models.BooleanField(default=False)

    def clean(self, *args, **kwargs):
        super(Task, self).clean()
        if self.deadline:
            if self.deadline < timezone.now():
                raise ValidationError('Deadline time must be later than now.')

    @logg('Added subtask')
    def add_subtask(self, task):
        self.subtasks.add(task)
        self.save()

    @logg('Copied task')
    def get_copy(self):
        copied = deepcopy(self)
        copied.id = None
        copied.save()
        for task in self.subtasks.all():
            copied.add_subtask(task)
        copied.save()
        return copied

    @logg('Finished task')
    def finish(self):
        self.status = Status.FINISHED
        self.save()
        for task in self.subtasks.all():
            task.finish()

    @logg('Unfinished taks')
    def unfinish(self):
        self.status = Status.UNFINISHED
        self.save()
        for task in self.subtasks.all():
            task.unfinish()

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
            if self.deadline < timezone.now() and self.status == Status.UNFINISHED:
                self.status = Status.OVERDUE
                call('Overdue task', self.info)
                return self

    @logg('Archived task')
    def pass_to_archive(self):
        self.archived = True

        self.save()

    @logg('Restored task')
    def restore_from_archive(self):
        self.archived = False
        self.unfinish()
        self.created_at = datetime.now().date()
        self.deadline = None
        self.save()

    @logg('Added performer to task')
    def add_performer(self, user_nickname):
        self.performers.append(user_nickname)
        self.save()

    @logg('Removed performer')
    def remove_performer(self, user_nickname):
        self.performers.remove(user_nickname)
        self.save()

    def __str__(self):
        return '{} {}'.format(self.info, self.deadline if self.deadline else 'no deadline')
