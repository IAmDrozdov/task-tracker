import os
import unittest

from calelib import configure_database

configure_database('calelib.database_settings.testing_settings')
from calelib.crud import Calendoola

from calelib.models import (Task,
                            Customer,
                            Plan,
                            Reminder, )

from django.utils import timezone


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.db = Calendoola()
        self.username = 'test_user'
        self.db.create_user(self.username)

    def tearDown(self):
        Task.objects.all().delete()
        Plan.objects.all().delete()
        Reminder.objects.all().delete()
        Customer.objects.all().delete()
        if os.path.exists('config.ini'):
            os.remove('config.ini')

    def test_create_task(self):
        self.db.create_task(self.username, info='test_info')
        self.assertTrue(self.db.get_tasks(self.username))

    def test_remove_task(self):
        self.db.create_task(self.username, info='test_info')
        self.db.remove_task(self.username, self.db.get_tasks(self.username).first().pk)
        self.assertFalse(self.db.get_tasks(self.username))

    def test_get_tasks_by_tag(self):
        for i in range(7):
            self.db.create_task(self.username, info=f'test_task{i}', tags='test tag') \
                if i < 3 else self.db.create_task(self.username, info=f'test_task{i}', tags='notags')

        self.assertEqual(3, self.db.get_tasks(self.username, tags='test tag').count())

    def test_get_tasks_by_info(self):
        for i in range(7):
            self.db.create_task(self.username, info=f'test_task') \
                if i < 3 else self.db.create_task(self.username, info=f'test_{i}task')

        self.assertEqual(3, self.db.get_tasks(self.username, info='test_task').count())

    def test_get_tasks_by_id(self):
        self.db.create_task(self.username, info='test_info')
        self.assertTrue(self.db.get_tasks(self.username).first().pk)

    def test_get_tasks_by_archive(self):
        for i in range(7):
            self.db.create_task(self.username, info=f'test_task')
        for task in self.db.get_tasks(self.username):
            task.pass_to_archive()

        self.assertEqual(7, self.db.get_tasks(self.username, archive=True).count())

    def test_change_task(self):
        self.db.create_task(self.username, info='test_task')
        self.db.change_task(self.username, self.db.get_tasks(self.username).first().pk, info='new_info')
        self.assertEqual(self.db.get_tasks(self.username).first().info, 'new_info')

    def test_get_plans_by_id(self):
        self.db.create_plan(self.username, info='test_plan', period_value={'day': 2}, period_type='d')
        self.assertTrue(self.db.get_plans(self.username, self.db.get_plans(self.username).first().pk))

    def test_get_plans(self):
        for i in range(5):
            self.db.create_plan(self.username, info='test_plan', period_value={'day': 2}, period_type='d')
        self.assertEqual(5, self.db.get_plans(self.username).count())

    def test_remove_plan(self):
        self.db.create_plan(self.username, info='test_plan', period_value={'day': 2}, period_type='d')
        self.db.remove_plan(self.username, self.db.get_plans(self.username).first().pk)
        self.assertFalse(self.db.get_plans(self.username))

    def test_create_plan(self):
        self.db.create_plan(self.username, info='test_plan', period_value={'day': 2}, period_type='d')
        self.assertTrue(self.db.get_plans(self.username))

    def test_change_plan(self):
        self.db.create_plan(self.username, info='test_plan', period_value={'day': 2}, period_type='d')
        self.db.change_plan(self.username, self.db.get_plans(self.username).first().pk, info='new_info')
        self.assertEqual(self.db.get_plans(self.username).first().info, 'new_info')

    def test_create_user(self):
        self.db.create_user('new_user')
        self.assertIn('new_user', [u.nickname for u in self.db.get_users()])

    def test_remove_user(self):
        self.db.remove_user('test_user')
        self.assertNotIn('test_user', [u.nickname for u in self.db.get_users()])

    def test_get_users_by_id(self):
        self.assertEqual('test_user', self.db.get_users('test_user').nickname)

    def test_get_users(self):
        self.db.create_user('new_user')
        self.assertEqual(2, self.db.get_users().count())

    def test_create_reminder(self):
        self.db.create_reminder(self.username, remind_type='m', remind_before=2)
        self.assertTrue(self.db.get_reminders(self.username))

    def test_get_reminder_by_id(self):
        self.db.create_reminder(self.username, remind_type='m', remind_before=2)
        self.assertTrue(self.db.get_reminders(self.username, self.db.get_reminders(self.username).first().pk))

    def test_get_reminders(self):
        for i in range(5):
            self.db.create_reminder(self.username, remind_type='m', remind_before=2)

        self.assertEqual(5, self.db.get_reminders(self.username).count())

    def test_change_reminder(self):
        self.db.create_reminder(self.username, remind_type='m', remind_before=2)
        self.db.change_reminder(self.username, self.db.get_reminders(self.username).first().pk, remind_value=20)
        self.assertEqual(20, self.db.get_reminders(self.username,
                                                   self.db.get_reminders(self.username).first().pk).remind_before)

    def test_add_completed_task(self):
        task = Task.objects.create(info='test_task')
        self.db.add_completed(self.username, 'task', task)
        self.assertTrue(self.db.get_tasks(self.username))

    def test_add_completed_plan(self):
        plan = Plan.objects.create(info='test_plan')
        self.db.add_completed(self.username, 'plan', plan)
        self.assertTrue(self.db.get_plans(self.username))

    def test_add_completed_reminder(self):
        reminder = Reminder.objects.create(remind_type='m', remind_before=2)
        self.db.add_completed(self.username, 'reminder', reminder)
        self.assertTrue(self.db.get_reminders(self.username))

    def test_get_sorted_tasks_desc(self):
        for i in range(7):
            self.db.create_task(self.username, info=f'test_task{i}',
                                deadline=timezone.now() + timezone.timedelta(days=i))

        self.assertEqual(list(reversed([f'test_task{i}' for i in range(7)])),
                         [t.info for t in self.db.get_sorted_tasks(self.username, 'deadline', 'desc')])
