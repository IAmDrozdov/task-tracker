from calelib.constants import Constants
from calelib.logger import logg
from calelib.notification import call
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Reminder(models.Model):
    remind_before = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    remind_type = models.CharField(
        max_length=6,
        choices=[
            (Constants.REMIND_MINUTES, 'minutes'),
            (Constants.REMIND_HOURS, 'hours'),
            (Constants.REMIND_DAYS, 'days'),
            (Constants.REMIND_MONTHS, 'months')
        ]
    )
    able = models.BooleanField(default=True)
    tasks = models.ManyToManyField('Task')
    owner = models.ForeignKey(
        'Customer',
        related_name='reminders',
        null=True,
        on_delete=models.CASCADE,
    )

    def get_tasks(self):
        return self.tasks.all()

    @logg('Applied task to reminder')
    def apply_task(self, task):
        self.tasks.add(task)

    @logg('Detached task from reminder')
    def detach_task(self, task):
        self.tasks.remove(task)

    @logg('Checked reminder')
    def check_tasks(self):
        if self.able:
            for task in self.tasks.all():
                if self._get_delta(task.deadline) < timezone.now():
                    call(task.info, self.__str__().replace('before', 'after'))
                    self.tasks.remove(task)

    def _get_delta(self, date):
        if self.remind_type == Constants.REMIND_MONTHS:
            return date - relativedelta(months=self.remind_before)
        elif self.remind_type == Constants.REMIND_DAYS:
            return date - relativedelta(days=self.remind_before)
        elif self.remind_type == Constants.REMIND_HOURS:
            return date - relativedelta(hours=self.remind_before)
        else:
            return date - relativedelta(minutes=self.remind_before)

    @logg('Changed information about reminder')
    def update(self, remind_type, remind_before):
        if remind_before:
            self.remind_before = remind_before
        if remind_type:
            self.remind_type = remind_type
        self.save()

    @logg('Changed reminder state')
    def set_state(self):
        self.able = not self.able
        self.save()

    def __str__(self):
        def humanize_type():
            if self.remind_type == Constants.REMIND_MONTHS:
                human_like = 'month'
            elif self.remind_type == Constants.REMIND_DAYS:
                human_like = 'day'
            elif self.remind_type == Constants.REMIND_HOURS:
                human_like = 'hour'
            else:
                human_like = 'minute'

            return human_like if self.remind_before == 1 else human_like + 's'

        return 'Before {} {}'.format(self.remind_before, humanize_type())
