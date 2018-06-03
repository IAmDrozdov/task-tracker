#!/usr/bin/env python3.6
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-


from parser import create_parser

import argcomplete
import console_operations as co
import django.core.exceptions as django_ex
from calelib import Config, Constants, Database, configure_logger


def main():
    cfg = Config(Constants.CONFIG_FILE_PATH)
    log_path = cfg.get_config_field('logging_path')
    pid_path = cfg.get_config_field('pid_path')
    log_level = cfg.get_config_field('logging_level')
    log_format = cfg.get_config_field('logging_format')
    configure_logger(log_path, log_format, log_level)
    parser = create_parser()
    db = Database()
    argcomplete.autocomplete(parser)
    namespace = parser.parse_args()
    #######################################
    if namespace.target == 'user':
        if namespace.command == 'add':
            co.operation_user_add(db, namespace.nickname, namespace.force, cfg)
        elif namespace.command == 'login':
            co.operation_user_login(namespace.nickname, cfg)
        elif namespace.command == 'logout':
            co.operation_user_logout(cfg)
        elif namespace.command == 'remove':
            co.operation_user_remove(db, namespace.nickname)
        elif namespace.command == 'info':
            co.operation_user_info(cfg)
        return
    #######################################
    try:
        db.current_user = cfg.get_config_field('current_user')
    except django_ex.ObjectDoesNotExist:
        print('You did not sign in. Please login')
        return
    #######################################
    if namespace.daemon:
        co.run_daemon(db, pid_path)
        return
    elif namespace.stop_daemon:
        co.stop_daemon(pid_path)
    #######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            co.operation_task_add(db, namespace.description, namespace.priority, namespace.deadline,
                                  namespace.tags, namespace.subtask)
        elif namespace.command == 'remove':
            co.operation_task_remove(db, namespace.id)
        elif namespace.command == 'show':
            co.operation_task_show(db, namespace.to_show, namespace.selected, namespace.colored)
        elif namespace.command == 'finish':
            co.operation_task_finish(db, namespace.id)
        elif namespace.command == 'move':
            co.operation_task_move(db, namespace.id_from, namespace.id_to)
        elif namespace.command == 'change':
            co.operation_task_change(db, namespace.id, namespace.info, namespace.deadline, namespace.priority,
                                     namespace.status, namespace.append_tags, namespace.remove_tags)
        elif namespace.command == 'share':
            co.operation_task_share(db, namespace.id_from, namespace.nickname_to)
        elif namespace.command == 'restore':
            co.operation_task_restore(db, namespace.id)
        elif namespace.command == 'unshare':
            co.operation_task_unshare(db, namespace.id)
    #######################################
    elif namespace.target == 'calendar':
        co.operation_calendar_show(db.get_tasks(), namespace.date[0], namespace.date[1])
    #######################################
    elif namespace.target == 'plan':
        if namespace.command == 'add':
            co.operation_plan_add(db, namespace.description, namespace.period_type, namespace.period_value,
                                  namespace.time)
        elif namespace.command == 'show':
            co.operation_plan_show(db, namespace.id, namespace.colored)
        elif namespace.command == 'remove':
            co.operation_plan_remove(db, namespace.id)
        elif namespace.command == 'change':
            co.operation_plan_change(db, namespace.id, namespace.info, namespace.period_type, namespace.period_value,
                                     namespace.time)
    #######################################
    # co.restart_daemon(db, pid_path)
    # Task.objects.all().delete()
    # User.objects.all().delete()
    from calelib.models import Plan
    import os


if __name__ == '__main__':
    main()
