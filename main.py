#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from lib import database, calendar_custom, plan_func, datetime_parser, task_func
from parser import create_parser
from lib.user import User
from lib.plan import Plan
from lib.task import Task


def main():
    db = database.Database('database.json')

    parser = create_parser()
    namespace = parser.parse_args()
    #######################################
    if namespace.target == 'user':
        if namespace.command == 'create':
            db.add_user(User(namespace.nickname))
            if namespace.force:
                db.set_current_user(namespace.nickname)
        elif namespace.command == 'login':
            db.set_current_user(namespace.nickname)
        elif namespace.command == 'logout':
            db.remove_current_user()
        elif namespace.command == 'remove':
            db.remove_user(namespace.nickname)
        elif namespace.command == 'info':
            db.get_current_user().print()
    #######################################
    if namespace.daemon:
        for plan in db.get_plans():
            plan.check(db)
        return
    #######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            task_func.operation_task_add(namespace, current.tasks)
        elif namespace.command == 'remove':
            db.remove_task(namespace.id)
        elif namespace.command == 'show':
            task_func.operation_task_show(current.tasks, namespace)
        elif namespace.command == 'finish':
            task_func.operation_task_finish(current.tasks, namespace)
        elif namespace.command == 'move':
            task_func.operation_task_move(current.tasks, namespace)
        elif namespace.command == 'change':
            task_func.operation_task_change(current.tasks, namespace)
        elif namespace.command == 'share':
            task_func.operation_task_share(current.tasks, db, namespace)
    #######################################
    elif namespace.target == 'calendar':
        calendar_custom.print_month_calendar(current.tasks, namespace.date[0], namespace.date[1])
    #######################################
    elif namespace.target == 'plan':
        if namespace.command == 'add':
            period_options = datetime_parser.parse_period(namespace.period)
            time = datetime_parser.parse_time(namespace.time) if namespace.time else None
            db.add_plan(Plan(info=namespace.description, period=period_options[0],
                             period_type=period_options[1], time_in=time))
        elif namespace.command == 'show':
            if namespace.id:
                print(db.get_plans(namespace.id))
            else:
                for plan in db.get_plans():
                    plan.colored_print(namespace.colored)
        elif namespace.command == 'remove':
            db.remove_plan(namespace.id)


if __name__ == '__main__':
    main()
