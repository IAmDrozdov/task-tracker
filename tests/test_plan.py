import os
import unittest

from calelib import configure_database
from django.utils import timezone

configure_database('calelib.database_settings.testing_settings')
from calelib.models import (Task,
                            Plan, )


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(info='test plan', period_type='d')
        self.plan.period = {'day': 2}
        self.plan.save()

    def tearDown(self):
        Task.objects.all().delete()
        Plan.objects.all().delete()
        if os.path.exists('config.ini'):
            os.remove('config.ini')

    def test_create_task(self):
        task = self.plan.create_task()
        self.assertIn(task, Task.objects.all())

    def test_remove_task(self):
        Task.objects.create(info='test_task', plan_id=self.plan.pk)
        self.plan.remove_task()
        self.assertFalse(Task.objects.all())

    def test_check_last_create_day(self):
        self.plan.last_create = timezone.now()
        self.plan.save()
        self.assertTrue(self.plan.check_last_create_day())

    def test_check_time_false(self):
        self.plan.time_at = (timezone.now() + timezone.timedelta(hours=1)).time()
        self.plan.save()
        self.assertFalse(self.plan.check_time())

    def test_time_true(self):
        self.plan.time_at = (timezone.now() - timezone.timedelta(hours=1)).time()
        self.plan.save()
        self.assertTrue(self.plan.check_time())

    def test_check_uncreated_weekday_type(self):
        self.plan.period_type = 'wd'
        self.plan.period = {'days': [timezone.now().weekday()]}
        self.plan.save()
        self.assertTrue(self.plan.check_uncreated())

    def test_check_uncreated_month_type(self):
        self.plan.period_type = 'm'
        self.plan.period = {'day': timezone.now().day,
                            'months': [timezone.now().month]}
        self.assertTrue(self.plan.check_uncreated())

    def test_check_created_days(self):
        Task.objects.create(info='test_task', plan_id=self.plan.pk)
        self.plan.save()
        self.plan.check_created_days()
        self.assertTrue(Task.objects.all())

    def test_check_created_wdays(self):
        Task.objects.create(info='test_task', plan_id=self.plan.pk)
        self.plan.period = {'days': [timezone.now().weekday() + 1]}
        self.plan.save()
        self.plan.check_created_wdays()
        self.assertFalse(Task.objects.all())

    def test_check_created_months(self):
        Task.objects.create(info='test_task', plan_id=self.plan.pk)
        self.plan.period = {'months': [timezone.now().month + 1]}
        self.plan.save()
        self.plan.check_created_months()
        self.assertFalse(Task.objects.all())

    def test_check_set_state(self):
        self.plan.set_state()
        self.assertFalse(self.plan.able)

    def test_check_update(self):
        self.plan.update(info='new_info',
                         period_type='wd',
                         period_value={'days': [1, 2]})
        self.assertEqual(self.plan.info, 'new_info')
        self.assertEqual(self.plan.period_type, 'wd')
        self.assertEqual(self.plan.period, {'days': [1, 2]})
