#!/usr/bin/env python3.6
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-


import argcomplete

from calendoola_app.console import console_operations as co
from calendoola_app.console.parser import create_parser
from calendoola_app.lib.database import Database
from calendoola_app.lib.constants import Constants as const
from calendoola_app.lib.config import Config
from calendoola_app.lib.daemon import Daemon


def main():
    cfg = Config(const.CONFIG_FILE_PATH)
    db = Database(cfg.get_config_field('database_path'))
    daemon = Daemon(cfg.get_config_field('pid_path'))
    log = cfg.get_config_field('logger_output_path')
    parser = create_parser()
    argcomplete.autocomplete(parser)
    namespace = parser.parse_args()
    #######################################
    if namespace.target == 'user':
        if namespace.command == 'add':
            co.operation_user_add(db, namespace.nickname, namespace.force)
        elif namespace.command == 'login':
            co.operation_user_login(db, namespace.nickname)
        elif namespace.command == 'logout':
            co.operation_user_logout(db)
        elif namespace.command == 'remove':
            co.operation_user_remove(db, namespace.nickname)
        elif namespace.command == 'info':
            co.operation_user_info(db)
    #######################################
    if namespace.daemon:
        daemon.run(co.check_plans, db)
        return
    elif namespace.stop_daemon:
        daemon.stop()
    #######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            co.operation_task_add(db, namespace.description, namespace.priority, namespace.deadline,
                                  namespace.tags, namespace.subtask)
        elif namespace.command == 'remove':
            co.operation_task_remove(db, namespace.id)
        elif namespace.command == 'show':
            co.operation_task_show(db, namespace.to_show, namespace.selected, namespace.all, namespace.colored)
        elif namespace.command == 'finish':
            co.operation_task_finish(db, namespace.id)
        elif namespace.command == 'move':
            co.operation_task_move(db, namespace.id_from, namespace.id_to)
        elif namespace.command == 'change':
            co.operation_task_change(db, namespace.id, namespace.info, namespace.deadline, namespace.priority,
                                     namespace.status, namespace.append_tags, namespace.remove_tags)
        elif namespace.command == 'share':
            co.operation_task_share(db, namespace.id_from, namespace.nickname_to, namespace.delete, namespace.track)
        elif namespace.command == 'restore':
            co.operation_task_restore(db, namespace.id)
    #######################################
    elif namespace.target == 'calendar':
        co.operation_calendar_show(db.get_tasks(), namespace.date[0], namespace.date[1])
    #######################################
    elif namespace.target == 'plan':
        if namespace.command == 'add':
            co.operation_plan_add(db, namespace.description, namespace.period, namespace.time)
        elif namespace.command == 'show':
            co.operation_plan_show(db, namespace.id, namespace.colored)
        elif namespace.command == 'remove':
            co.operation_plan_remove(db, namespace.id)
    daemon.restart(co.check_plans, db)


if __name__ == '__main__':
    main()
