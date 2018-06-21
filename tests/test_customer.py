import os
import unittest

from calelib import configure_database

configure_database('calelib.database_settings.testing_settings')

from calelib.models import (Task,
                            Customer,
                            Plan,
                            Reminder, )


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.user = Customer.objects.create(nickname='test_user')

    def tearDown(self):
        Task.objects.all().delete()
        Plan.objects.all().delete()
        Reminder.objects.all().delete()
        Customer.objects.all().delete()
        if os.path.exists('config.ini'):
            os.remove('config.ini')

    def test_add_task(self):
        task = Task.objects.create(info='test_task')
        self.user.add_task(task)
        self.assertIn(task, self.user.tasks.all())

    def test_task_remove(self):
        task = Task.objects.create(info='test_task')
        self.user.add_task(task)
        self.user.remove_task(task)
        self.assertNotIn(task, self.user.tasks.all())
        user2 = Customer.objects.create(nickname='test_user_1')
        task = Task.objects.create(info='test_task')
        self.user.add_task(task)
        user2.apply_task(task)
        self.user.remove_task(task)
        self.assertNotIn(task, self.user.tasks.all())
        self.assertNotIn(task, user2.tasks.all())

    def test_shared_task_remove(self):
        user2 = Customer.objects.create(nickname='test_user_1')
        task = Task.objects.create(info='test_task')
        self.user.add_task(task)
        user2.apply_task(task)
        self.user.remove_task(task)
        self.assertNotIn(task, self.user.tasks.all())
        self.assertNotIn(task, user2.tasks.all())

    def test_applied_task_remove(self):
        user2 = Customer.objects.create(nickname='test_user_1')

        task = Task.objects.create(info='test_task')
        self.user.add_task(task)
        user2.apply_task(task)
        user2.remove_task(task)
        self.assertIn(task, self.user.tasks.all())
        self.assertNotIn(task, user2.tasks.all())

    def test_add_plan(self):
        plan = Plan.objects.create(info='test_plan', period_type='d', _period=2)
        self.user.add_plan(plan)
        self.assertIn(plan, self.user.plans.all())

    def test_plan_remove(self):
        plan = Plan.objects.create(info='test_plan', period_type='d', _period=2)
        self.user.add_plan(plan)
        self.user.remove_plan(plan.pk)
        self.assertNotIn(plan, self.user.plans.all())

    def test_add_reminder(self):
        reminder = Reminder.objects.create(remind_type='m', remind_before=3)
        self.user.add_reminder(reminder)
        self.assertIn(reminder, self.user.reminders.all())

    def test_remove_reminder(self):
        reminder = Reminder.objects.create(remind_type='m', remind_before=3)
        self.user.add_reminder(reminder)
        self.user.remove_reminder(reminder.pk)
        self.assertNotIn(reminder, self.user.reminders.all())

    def test_apply_task(self):
        task = Task.objects.create(info='test_task')
        self.user.apply_task(task)
        self.assertIn(task, self.user.shared_tasks.all())

    def test_detach_task(self):
        task = Task.objects.create(info='test_task')
        self.user.apply_task(task)
        self.user.detach_task(task)
        self.assertNotIn(task, self.user.shared_tasks.all())
