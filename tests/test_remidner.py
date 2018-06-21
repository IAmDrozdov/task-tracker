import os
import unittest

from calelib import configure_database

configure_database('calelib.database_settings.testing_settings')
from django.utils import timezone
from calelib.models import (Task,
                            Reminder, )


class TestReminder(unittest.TestCase):
    def setUp(self):
        self.reminder = Reminder.objects.create(remind_before=1, remind_type='m')
        self.task = Task.objects.create(info='test_task')

    def tearDown(self):
        Task.objects.all().delete()
        Reminder.objects.all().delete()
        if os.path.exists('config.ini'):
            os.remove('config.ini')

    def test_apply_task(self):
        self.reminder.apply_task(self.task)
        self.assertIn(self.task, self.reminder.get_tasks())

    def test_get_tasks(self):
        self.reminder.apply_task(self.task)
        self.assertListEqual(list(self.reminder.get_tasks()), list(self.reminder.tasks.all()))

    def test_detach_task(self):
        self.reminder.apply_task(self.task)
        self.reminder.detach_task(self.task)
        self.assertFalse(self.reminder.get_tasks())

    def test_check_tasks(self):
        self.task.deadline = timezone.now()
        self.task.save()
        self.reminder.apply_task(self.task)
        self.reminder.check_tasks()
        self.assertFalse(self.reminder.get_tasks())

    def test_check_update(self):
        self.reminder.update('h', 14)
        self.assertEqual(self.reminder.remind_type, 'h')
        self.assertEqual(self.reminder.remind_before, 14)

    def test_check_state(self):
        self.reminder.set_state()
        self.assertFalse(self.reminder.able)
