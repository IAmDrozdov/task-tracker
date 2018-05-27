import unittest
from datetime import datetime

from calelib import Constants
from calelib import Task
from calelib import date_parse as dp


class DatetimeParserTests(unittest.TestCase):
    def test_get_deadline(self):
        self.assertEqual(dp.get_deadline('5 May'), '2019-05-05 00:00:00')
        self.assertEqual(dp.get_deadline('30 May'), '2018-05-30 00:00:00')

    def test_parse_iso_pretty(self):
        self.assertEqual(dp.parse_iso_pretty('2018-05-08 00:00:00'), '08 May')

    def test_parse_iso(self):
        self.assertEqual(dp.parse_iso('2018-05-08 00:00:00'), datetime(2018, 5, 8).date())

    def test_get_first_weekday(self):
        self.assertEqual(dp.get_first_weekday(5, 2018), 2)

    def test_get_weekday_number(self):
        self.assertEqual(dp.get_weekday_number('Monday'), 0)

    def test_get_weekday_word(self):
        self.assertEqual(dp.get_weekday_word(0), 'monday')

    def test_parse_period(self):
        self.assertEqual(dp.parse_period('day', '1'), {'period': 1, 'type': Constants.REPEAT_DAY})
        self.assertEqual(dp.parse_period('week', 'monday tuesday'),
                         {'period': [0, 1], 'type': Constants.REPEAT_WEEKDAY})
        self.assertEqual(dp.parse_period('month', '25 September May'),
                         {'period': {'day': 25, 'months': [9, 5]}, 'type': Constants.REPEAT_MONTH})
        self.assertEqual(dp.parse_period('year', '25 September'),
                         {'period': {'day': 25, 'month': 9}, 'type': Constants.REPEAT_YEAR})

    def test_parse_time(self):
        self.assertEqual(dp.parse_time('5'), {'hour': 5, 'minutes': None, 'with_minutes': False})
        self.assertEqual(dp.parse_time('5:20'), {'hour': 5, 'minutes': 20, 'with_minutes': True})

    def test_is_match(self):
        self.assertTrue(dp.is_match('2018-05-08 00:00:00', 5, 2018))

    def test_mark_dates(self):
        first_task = Task(info='no deadline')
        second_task = Task(info='with deadline', deadline='2018-05-08 00:00:00')
        self.assertEqual(dp.mark_dates([first_task, second_task], 5, 2018), [8])
