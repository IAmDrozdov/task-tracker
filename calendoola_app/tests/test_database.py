import os
import unittest

import calendoola_app.lib.custom_exceptions as ce
from calendoola_app.lib.constants import Constants as const
from calendoola_app.lib.database import Database
from calendoola_app.lib.config import Config
from calendoola_app.lib.models.plan import Plan
from calendoola_app.lib.models.task import Task
from calendoola_app.lib.models.user import User


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        cfg = Config(const.CONFIG_FILE_PATH)
        self.db_path = cfg.get_config_field('database_path')
        self.test_user = User(nickname='test')
        self.test_task = Task(info='test_task')
        self.test_subtask = Task(info='sub_test')
        self.test_subtask.parent_id = '1'
        self.test_plan = Plan(info='test_plan', period=5, period_type='d')
        self.db = Database(self.db_path)

    def test_get(self):
        self.db.add_user(self.test_user)
        self.assertEqual(self.db.get_users(self.test_user.nickname), self.test_user)
        self.assertEqual(self.db.get_users(), [self.test_user])

    def test_set_current_user(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.assertEqual(self.db.current_user, self.test_user.nickname)

    def test_add_user(self):
        self.db.add_user(self.test_user)
        self.assertIn(self.test_user, self.db.get_users())

    def test_get_current(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.assertEqual(self.db.get_current_user(), self.test_user)

    def test_check_exist(self):
        self.db.add_user(self.test_user)
        self.assertRaises(ce.UserAlreadyExists, self.db.check_user_exist, nickname=self.test_user.nickname)

    def test_remove_current_user(self):
        self.db.add_user(self.test_user)
        self.db.remove_current_user()
        self.assertIsNone(self.db.current_user)

    def test_remove_user(self):
        self.db.add_user(User(nickname='test_current'))
        self.db.set_current_user('test_current')
        self.db.add_user(self.test_user)
        self.db.remove_user(self.test_user.nickname)
        self.assertNotIn(self.test_user, self.db.get_users())

    def test_get_task(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.db.add_task(self.test_task)
        self.assertEqual(self.test_task, self.db.get_tasks(self.test_task.id))
        self.assertListEqual(self.db.get_tasks(), [self.test_task])

    def test_get_id(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.db.add_task(self.test_task)
        self.assertEqual(self.test_task.id, '1')

        self.db.add_task(self.test_subtask)
        self.assertEqual(self.test_subtask.id, '1_1')

    def test_add_task(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.db.add_task(self.test_task)
        self.assertIn(self.test_task, self.db.get_tasks())
        self.db.add_task(self.test_subtask)
        self.assertIn(self.test_subtask, self.test_task.subtasks)

    def test_change_task(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.db.add_task(self.test_task)
        self.db.change_task(self.test_task.id, info='test_changed')
        self.assertEqual(self.test_task.info, 'test_changed')

    def test_get_plan(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.db.add_plan(self.test_plan)
        self.assertEqual([self.test_plan], self.db.get_plans())
        self.assertEqual(self.test_plan, self.db.get_plans(self.test_plan.id))

    def test_add_plan(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.db.add_plan(self.test_plan)
        self.assertIn(self.test_plan, self.db.get_plans())

    def test_remove_plan(self):
        self.db.add_user(self.test_user)
        self.db.set_current_user(self.test_user.nickname)
        self.db.add_plan(self.test_plan)
        self.db.remove_plan(self.test_plan.id)
        self.assertNotIn(self.test_plan, self.db.get_plans())

    def tearDown(self):
        os.remove(self.db_path)
        if os.path.exists(const.CONFIG_FILE_PATH):
            os.remove(const.CONFIG_FILE_PATH)
