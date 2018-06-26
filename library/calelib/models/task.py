from calelib.constants import (Status,
                               Notifications, )
from calelib.custom_exceptions import CycleError
from calelib.logger import logg
from calelib.notification import Notification
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Task(models.Model):
    """
    Represents Task instance
    Fields:
        owner(Customer): Customer instance which created this reminder
        info(str): description of task
        created_at(datetime): date of creation task
        updated_at(datetime): date of updating info about task
        parent_task(Task): task in which subtasks container this task in
        tags(str): tags for task
        priority(int): importance of task(1..5)
        status(str): status of implementation
        deadline(datetime): date when task will be overdue
        plan(Plan): Plan instance what created this task
        archive(bool): field what shows should task be check
    """
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
        """Validation of deadline"""
        super(Task, self).clean()
        if self.deadline:
            if self.deadline < timezone.localtime():
                raise ValidationError('Deadline time must be later than now.')

    @logg('Added subtask')
    def add_subtask(self, task):
        """
        Add task to subtasks container
        Args:
            task(Task): completed instance of Task
        """
        self.subtasks.add(task)
        self.save()

    @logg('Finished task')
    def finish(self):
        """Set status to FINISH and archive to True of self and subtasks"""
        self.status = Status.FINISHED
        self.archived = True
        self.save()
        for task in self.subtasks.all():
            task.finish()

    @logg('Unfinished task')
    def restore(self):
        """Set status to UNFINISH and archive to False of self and subtasks"""

        self.status = Status.UNFINISHED
        self.archived = False
        self.created_at = timezone.localtime().date()
        self.deadline = None
        self.save()
        for task in self.subtasks.all():
            task.restore()

    @logg('Changed information about task')
    def update(self, info=None, deadline=None, priority=None, status=None, plus_tag=None, minus_tag=None):
        """Update information about task"""
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
        """Goes down and find task_id in subtasks"""
        for task in self.subtasks.all():
            if task.id == id:
                return True
            else:
                task.__rec_up(id)

    @logg('Task checked for cycles')
    def is_parent(self, id):
        """
        Check for cycles
        Args:
            id of prospective parent task
        """
        if self.__rec_up(id):
            raise CycleError
        else:
            return False

    @logg('''Checked task's deadline''')
    def check_deadline(self):
        """
        Check task for deadline overdue
        Return:
            notification
        """
        if self.deadline is not None:
            if self.deadline < timezone.localtime() and self.status == Status.UNFINISHED:
                self.status = Status.OVERDUE
                self.finish()
                return Notification(
                    title=Notifications.OVERDUE,
                    info=self.info
                )

    def __str__(self):
        return '{} {}'.format(self.info, self.deadline if self.deadline else 'no deadline')
