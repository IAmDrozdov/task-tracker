import os
import unittest

import calendoola_app.calendoola_lib.etc.custom_exceptions as ce
from calendoola_app.console.modules.console_operations import ConsoleOperations
from calendoola_app.calendoola_lib.modules.constants import Status
from calendoola_app.calendoola_lib.db.database import Database


class ConsoleOperationsTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_database.json'
        self.log_path = 'test_logs.log'
        self.pid_path = 'test_pid.ini'

        self.test_user_nickname = 'test'
        self.test_user_nickname_1 = 'test_1'
        self.test_task_info = 'test_task'
        self.test_task_sub_info = 'sub_test'
        self.test_plan_info = 'test_plan'

        self.db = Database(self.db_path)
        self.co = ConsoleOperations(self.log_path, self.pid_path, None)

    def test_operation_user_add(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, None)
        self.assertEqual(self.test_user_nickname, self.db.get_users().pop().nickname)

    def test_user_login(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, None)
        self.co.operation_user_login(self.db, self.test_user_nickname)
        self.assertEqual(self.db.get_current_user().nickname, self.test_user_nickname)

    def test_user_logout(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_user_logout(self.db)
        self.assertRaises(ce.UserNotAuthorized, self.db.get_current_user)

    def test_user_remove(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_user_remove(self.db, self.test_user_nickname)
        self.assertFalse(self.db.get_users())

    def test_task_add(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.assertEqual(self.test_task_info, self.db.get_tasks().pop().info)

    def test_task_remove(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_remove(self.db, '1')
        self.assertFalse(self.db.get_tasks())

    def test_task_finish_prim(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_finish(self.db, '1')
        self.assertFalse(self.db.get_tasks())
        self.assertEqual(self.db.get_tasks(archive=True).pop().status, Status.FINISHED)

    def test_task_finish_subs(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_add(self.db, self.test_task_sub_info, None, None, None, '1')
        self.co.operation_task_finish(self.db, '1')
        self.assertEqual(self.db.get_tasks('1', True).subtasks.pop().status, Status.FINISHED)

    def test_task_move_to_prim(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_add(self.db, self.test_task_sub_info, None, None, None, '1')
        self.co.operation_task_move(self.db, '1_1', '0')
        self.assertEqual(len(self.db.get_tasks()), 2)

    def test_task_move_subs(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_add(self.db, self.test_task_sub_info, None, None, None, '1')
        self.co.operation_task_add(self.db, self.test_task_sub_info + '1', None, None, None, '1')
        self.co.operation_task_move(self.db, '1_2', '1_1')
        self.assertTrue(self.db.get_tasks('1_1'))

    def test_task_change(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, 'tag_to_remove', None)
        self.co.operation_task_change(self.db, '1', 'new_info', '1 September', 4, 'new_status', 'new_tag, new_tag_1',
                                      'tag_to_remove')
        changed_task = self.db.get_tasks('1')
        self.assertEqual(changed_task.info, 'new_info')
        self.assertEqual(changed_task.deadline, '2018-09-01 00:00:00')
        self.assertEqual(changed_task.priority, 4)
        self.assertEqual(changed_task.status, 'new_status')
        self.assertIn('new_tag', changed_task.tags)
        self.assertIn('new_tag_1', changed_task.tags)
        self.assertNotIn('tag_to_remove', changed_task.tags)

    def test_task_share_without_deleting(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_user_add(self.db, self.test_user_nickname_1, False)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_share(self.db, '1', self.test_user_nickname_1, None, None)
        self.assertTrue(self.db.get_tasks())
        self.assertTrue(self.db.get_users(self.test_user_nickname_1).get_all_tasks())

    def test_task_share_with_deleting(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_user_add(self.db, self.test_user_nickname_1, False)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, 'tag_to_remove', None)
        self.co.operation_task_share(self.db, '1', self.test_user_nickname_1, True, None)
        self.assertFalse(self.db.get_tasks())
        self.assertTrue(self.db.get_users(self.test_user_nickname_1).get_all_tasks())

    def test_task_share_with_track(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_user_add(self.db, self.test_user_nickname_1, False)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_share(self.db, '1', self.test_user_nickname_1, None, True)
        self.assertTrue(self.db.get_tasks().pop().user)
        self.assertTrue(self.db.get_users(self.test_user_nickname_1).get_all_tasks().pop().owner)

    def test_task_unshare(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_user_add(self.db, self.test_user_nickname_1, False)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_share(self.db, '1', self.test_user_nickname_1, None, True)
        self.co.operation_task_unshare(self.db, '1')
        self.assertFalse(self.db.get_tasks().pop().user)
        self.assertFalse(self.db.get_users(self.test_user_nickname_1).get_all_tasks())

    def test_task_restore(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_task_add(self.db, self.test_task_info, None, None, None, None)
        self.co.operation_task_finish(self.db, '1')
        self.co.operation_task_restore(self.db, '1')
        self.assertFalse(self.db.get_tasks(archive=True))
        self.assertTrue(self.db.get_tasks())
        self.co.operation_task_add(self.db, self.test_task_sub_info, None, None, None, '1')
        self.co.operation_task_finish(self.db, '1_1')
        self.co.operation_task_restore(self.db, '1')
        self.assertTrue(self.db.get_tasks().pop().subtasks)

    def test_plan_add(self):
        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_plan_add(self.db, self.test_plan_info, 'day', '5', None)
        self.assertTrue(self.db.get_plans())

    def test_plan_remove(self):

        self.co.operation_user_add(self.db, self.test_user_nickname, True)
        self.co.operation_plan_add(self.db, self.test_plan_info, 'day', '5', None)
        self.co.operation_plan_remove(self.db, '1')
        self.assertFalse(self.db.get_plans())

    def tearDown(self):
        os.remove(self.db_path)
        if os.path.exists(self.pid_path):
            os.remove(self.pid_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
