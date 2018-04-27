#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from lib import database, calendar_custom, plan_func, user_func, task_func
from parser import create_parser


def main():
    db = database.deserialize('database.json')
    parser = create_parser()
    namespace = parser.parse_args()
    #########################################
    if namespace.target == 'user':
        if namespace.command == 'create':
            user_func.operation_create_user(db, namespace)
            database.serialize(db, 'database.json')
            return
        elif namespace.command == 'login':
            user_func.operation_login_user(db, namespace)
            database.serialize(db, 'database.json')
            return
    if db['current_user']:
        for user in db['users']:
            if user.nickname == db['current_user']:
                current = user
                break
        else:
            db['current_user'] = None
            print('User does not exist')
            database.serialize(db, 'database.json')
            return
    else:
        print('use "user login" to sight in, or create new user using "user create"')
        return
    #########################################
    if namespace.daemon:
        for plan in user.plans:
            plan.check(user.tasks)

        database.serialize(db, 'database.json')
        return
        ######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            task_func.operation_task_add(namespace, current.tasks)
        elif namespace.command == 'remove':
            task_func.operation_user_remove(current.tasks, namespace)
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
    elif namespace.target == 'user':
        if namespace.command == 'logout':
            user_func.operation_user_logout(db)
        elif namespace.command == 'remove':
            user_func.operation_user_remove(db, namespace)
        elif namespace.command == 'info':
            current.print()
    elif namespace.target == 'plan':
        if namespace.command == 'add':
            plan_func.operation_plan_add(user.plans, namespace)
        elif namespace.command == 'show':
            if namespace.id:
                plan_func.operation_plan_show_id(user.plans, namespace)
            else:
                plan_func.operation_plan_show_all(user.plans, namespace)
        elif namespace.command == 'remove':
            plan_func.operation_plan_remove(user, namespace)
    database.serialize(db, 'database.json')


if __name__ == '__main__':
    main()
