from calelib.constants import Constants
from django.db import models


class Reminder(models.Model):
    remind_before = models.IntegerField(default=0)
    remind_type = models.CharField(max_length=6,
                                   choices=[
                                       (Constants.REMIND_MINUTES, 'minutes'),
                                       (Constants.REMIND_HOURS, 'hours'),
                                       (Constants.REMIND_DAYS, 'days'),
                                       (Constants.REMIND_MONTHS, 'months')
                                   ]
                                   )
    remind_period = models.IntegerField(null=True)
    tasks = models.ManyToManyField('Task')
