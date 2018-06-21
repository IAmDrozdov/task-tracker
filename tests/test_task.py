import os
import unittest

from calelib import configure_database
from django.utils import timezone

configure_database('calelib.database_settings.testing_settings')

from calelib.models import (Task,
                            Customer, )
from calelib import CycleError


class TestTask(unittest.TestCase):
    def setUp(self):
        self.user = Customer.objects.create(nickname='test_user')
        self.task = Task.objects.create(info='test_task')

    def tearDown(self):
        Task.objects.all().delete()
        Customer.objects.all().delete()
        if os.path.exists('config.ini'):
            os.remove('config.ini')

    def test_add_subtask(self):
        sub_task = Task.objects.create(info='new_sub')
        self.task.add_subtask(sub_task)
        self.assertIn(sub_task, self.task.subtasks.all())

    def test_finish(self):
        self.task.finish()
        self.assertEqual(self.task.status, 'Finished')

    def test_finish_wuth_sub(self):
        sub_task = Task.objects.create(info='new_sub')
        self.task.add_subtask(sub_task)
        self.task.finish()
        self.assertListEqual([t.status for t in self.task.subtasks.all()],
                             ['Finished'] * self.task.subtasks.all().count())

    def test_unfinish(self):
        self.task.finish()
        self.task.unfinish()
        self.assertEqual(self.task.status, 'Not finished')

    def test_unfinish_with_sub(self):
        sub_task = Task.objects.create(info='new_sub')
        self.task.add_subtask(sub_task)
        self.task.finish()
        self.task.unfinish()
        self.assertListEqual([t.status for t in self.task.subtasks.all()],
                             ['Not finished'] * self.task.subtasks.all().count())

    def test_update(self):
        now = timezone.now()
        self.task.update(info='new_info',
                         deadline=now,
                         priority=3)
        self.assertEqual(self.task.info, 'new_info')
        self.assertEqual(self.task.deadline, now)
        self.assertEqual(self.task.priority, 3)

    def test_parent_check_false(self):
        sub_task = Task.objects.create(info='new_sub')
        self.task.add_subtask(sub_task)
        self.assertFalse(sub_task.is_parent(self.task.pk))

    def test_is_parent_true(self):
        sub_task = Task.objects.create(info='new_sub')
        self.task.add_subtask(sub_task)
        with self.assertRaises(CycleError):
            self.task.is_parent(sub_task.pk)

    def test_check_deadline_when_deadline_none(self):
        self.assertFalse(self.task.check_deadline())

    def test_check_deadline(self):
        self.task.deadline = timezone.now()
        self.assertTrue(self.task.check_deadline())

    def test_pass_to_archive(self):
        self.task.pass_to_archive()
        self.assertTrue(self.task.archived)

    def test_pass_to_archive_with_sub(self):
        sub_task = Task.objects.create(info='new_sub')
        self.task.add_subtask(sub_task)
        self.task.pass_to_archive()
        self.assertListEqual([t.archived for t in self.task.subtasks.all()],
                             [True] * self.task.subtasks.all().count())

    def test_restore_from_archive(self):
        self.task.pass_to_archive()
        self.task.restore_from_archive()
        self.assertFalse(self.task.archived)

    def test_restore_from_archive_with_sub(self):
        sub_task = Task.objects.create(info='new_sub')
        self.task.add_subtask(sub_task)
        self.task.pass_to_archive()
        self.task.restore_from_archive()
        self.assertListEqual([t.archived for t in self.task.subtasks.all()],
                             [False] * self.task.subtasks.all().count())
