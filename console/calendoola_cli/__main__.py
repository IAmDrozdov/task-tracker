#!/usr/bin/env python3.6
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-
import configparser

from calelib import configure_database

configure_database()
from parser import create_parser

import argcomplete
import console_operations as co
import django.core.exceptions as django_ex
from calelib.crud import Calendoola


def main():
    parser = create_parser()
    db = Calendoola()
    argcomplete.autocomplete(parser)
    namespace = parser.parse_args()
    try:
        db.cfg.get_field('current_user')
    except configparser.NoOptionError:
        db.cfg.add_field('current_user')
    #######################################
    if namespace.target == 'user':
        if namespace.command == 'add':
            co.operation_user_add(db, namespace.nickname, namespace.force)
        elif namespace.command == 'login':
            co.operation_user_login(namespace.nickname, db)
        elif namespace.command == 'logout':
            co.operation_user_logout(db)
        elif namespace.command == 'remove':
            co.operation_user_remove(db, namespace.nickname)
        elif namespace.command == 'info':
            co.operation_user_info(db)
        return
    #######################################
    try:
        db.cfg.get_field('current_user')
    except django_ex.ObjectDoesNotExist:
        print('You did not sign in. Please login')
        return
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
        co.operation_calendar_show(db.get_tasks(db.cfg.get_field('current_user')), namespace.date[0], namespace.date[1])
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
    elif namespace.target == 'reminder':
        if namespace.command == 'add':
            co.operation_reminder_add(db, namespace.remind_type, namespace.remind_value)
        elif namespace.command == 'remove':
            co.operation_reminder_remove(db, namespace.id)
        elif namespace.command == 'apply':
            co.operation_reminder_apply_task(db, namespace.reminder_id, namespace.task_id)
        elif namespace.command == 'detach':
            co.operation_reminder_detach_task(db, namespace.reminder_id, namespace.task_id)
        elif namespace.command == 'show':
            co.operation_reminder_show(db, namespace.id)
        elif namespace.command == 'change':
            co.operation_reminder_change(db, namespace.id, namespace.remind_type, namespace.remind_value)

    co.check_instances(db)


if __name__ == '__main__':
    main()
