import os
import unittest

from calendoola_app.lib.database import Database
from calendoola_app.lib.models.user import User
from calendoola_app.lib.models.task import Task
from calendoola_app.lib.models.plan import Plan
from calendoola_app.lib.constants import Constants as const


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.db.add_user(User(nickname='sasha'))

    def test_test(self):
        self.assertEqual('2', str(2))

    def tearDown(self):
        os.remove('config.ini')
        os.remove('database.json')
