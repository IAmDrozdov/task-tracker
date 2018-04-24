#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from lib import database, datetime_parser, calendar_custom
from parser import create_parser
from lib.task import Task
from lib.user import User
from lib.plan import Plan
import re
from _datetime import datetime
import copy


def rec_task_show_all(container, options):
    if container:
        for task in container:
            task.table_print(options.colored)
            rec_task_show_all(task.subtasks, options)


def rec_task_show_id(container, options):
    if container:
        for task in container:
            if task.id == options.choosen:
                task.table_print(options.colored)
                rec_task_show_all(task.subtasks, options)
                return
            rec_task_show_id(task.subtasks, options)


def rec_task_show_tags(container, options):
    if container:
        for task in container:
            if all(elem in task.tags for elem in options.choosen.split()):
                task.table_print(options.colored)
            rec_task_show_tags(task.subtasks, options)


def rec_task_add_sub(container, options):
    if container:
        for task in container:
            if task.id == options.subtask:
                new_task = Task(info=options.description,
                                id=task.id + '_' + Task.get_actual_index(task.subtasks),
                                deadline=datetime_parser.get_deadline(
                                    options.deadline) if options.deadline else None,
                                tags=re.sub("[^\w]", " ",  options.tags).split() if options.tags else [],
                                priority=options.priority if options.priority else 1,
                                indent=task.id.count('_') + 1)
                task.subtasks.append(new_task)
                return
            rec_task_add_sub(task.subtasks, options)


def operation_task_add(options, container):
    if options.subtask:
        rec_task_add_sub(container, options)
    elif options.periodic:
        pass
    else:
        new_task = Task(info=options.description,
                        id=Task.get_actual_index(container, False),
                        deadline=datetime_parser.get_deadline(options.deadline) if options.deadline else None,
                        tags=re.sub("[^\w]", " ",  options.tags).split() if options.tags else [],
                        priority=options.priority if options.priority else 1)
        container.append(new_task)
    database.serialize(container, 'database.json')


def operation_taks_show(container, options):
    if len(container) == 0:
        print('Nothing to show')
    if options.to_show == 'id':
        rec_task_show_id(container, options)
    elif options.to_show == 'tag':
        rec_task_show_tags(container, options)
    elif options.all:
        rec_task_show_all(container, options)
    else:
        for index, task in enumerate(container):
            task.table_print(options.colored)
            if index == 9:
                return


def rec_task_delete(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                container.remove(task)
                return
            operation_remove(task.subtasks, options)


def operation_remove(container, options):
    rec_task_delete(container, options)
    database.serialize(container, 'database.json')


def rec_task_finish_all(container):
    if container:
        for task in container:
            task.status = 'finished'
            rec_task_finish_all(task.subtasks)


def rec_task_finish(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                task.status = 'finished'
                rec_task_finish_all(task.subtasks)
            rec_task_finish(task.subtasks, options)


def operation_task_finish(container, options):
    rec_task_finish(container, options)
    database.serialize(container, 'database.json')


def rec_task_find(container, idx_mass):
    for task in container:
        if int(task.id.split('_')[len(task.id.split('_')) - 1]) == int(idx_mass[0]):
            if len(idx_mass) > 1:
                return rec_task_find(task.subtasks, idx_mass[1:])
            else:
                return task


def rec_task_move_sub(owner):
    if owner.subtasks:
        for task in owner.subtasks:
            task.id = owner.id + '_' + str(int(Task.get_actual_index(owner.subtasks, True)) - 1)
            task.indent = owner.id.count('_') + 1
            rec_task_move_sub(task)


def operation_task_move(container, options):
    task_from = rec_task_find(container, options.id_from.split('_'))
    task_to = rec_task_find(container, options.id_to.split('_'))
    if task_to and task_from:
        task_from.id = task_to.id + '_' + Task.get_actual_index(task_to.subtasks)
        task_from.indent = task_from.id.count('_')
        rec_task_move_sub(task_from)
        temp_task = copy.deepcopy(task_from)
        rec_task_delete(container, task_from)
        task_to.subtasks.append(temp_task)
        database.serialize(container, 'database.json')


def rec_task_change(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                if options.deadline:
                    task.deadline = datetime_parser.get_deadline(options.deadline)
                if options.info:
                    task.info = options.info
                if options.priority:
                    task.priority = options.priority
                if options.status:
                    task.status = options.status
                if options.append_tags:
                    for tag in re.sub("[^\w]", " ",  options.append_tags).split():
                        task.tags.append(tag)
                    task.tags = list(set(task.tags))
                if options.remove_tags:
                    for tag in re.sub("[^\w]", " ", options.remove_tags).split():
                        if tag in task.tags:
                            task.tags.remove(tag)
                task.changed = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                return
            rec_task_change(task.subtasks, options)


def operation_task_change(container, options):
    rec_task_change(container, options)
    database.serialize(container, 'database.json')


def operation_create_user(container, options):
    for user in container['users']:
        if user.nickname == options.nickname:
            print('A user with the nickname "{}" already exists.'. format(options.nickname))
            return
    new_user = User(nickname=options.nickname)
    container['users'].append(new_user)
    if options.force:
        container['current_user'] = new_user.nickname
    database.serialize(container, 'database.json')


def operation_login_user(container, options):
    for user in container['users']:
        if user.nickname == options.nickname:
            container['current_user'] = options.nickname
            break
    else:
        print('User does not exist')


def operation_logout_user(container):
    for user in container['users']:
        if user.nickname == container['current_user']:
            container['current_user'] = None
            break
    else:
        print('User does not exist')


def operation_remove_user(container, options):
    for user in container['users']:
        if user.nickname == options.nickname:
            container['users'].remove(user)

    else:
        print('User does not exist')


def rec_default_subs(new_task):
    if new_task.subtasks:
        for index, task in enumerate(new_task.subtasks):
            task.id = new_task.id + '_' + str(index + 1)
            task.indent = task.id.count('_')
            rec_default_subs(task)


def operation_task_share(current_user_tasks, container, options):
    task_from = rec_task_find(current_user_tasks, options.id_from.split('_'))
    for user in container['users']:
        if user.nickname == options.nickname_to:
            user_to = user
            break
    else:
        print('Nowhere to send task')
        return
    new_task = copy.deepcopy(task_from)
    new_task.id = Task.get_actual_index(user_to.tasks, False)
    new_task.indent = 0
    rec_default_subs(new_task)
    user_to.tasks.append(new_task)
    if options.delete:
        current_user_tasks.remove(task_from)


def operation_plan_add(container, options):
    new_plan = Plan(info=options.description, id=Task.get_actual_index(container))
    container.append(new_plan)
    Plan.check(container)


def operation_plan_remove(container, options):
    for plan in container:
        if plan.id == options.id:
            container.remove(plan)
            return
    else:
        print('Nothing to delete.')


def operation_plan_show_id(container, options):
    for plan in container:
        if plan.id == options.id:
            print(plan)
            return
    else:
        print('Nothing to show')


def operation_plan_show_all(container, options):
    if len(container) != 0:
        for plan in container:
            Plan.colored_print(plan, options.colored)
    else:
        print('No plans')


def main():
    db = database.deserialize('database.json')
    parser = create_parser()
    namespace = parser.parse_args()
    if namespace.target == 'user':
        if namespace.command == 'create':
            operation_create_user(db, namespace)
            return
        elif namespace.command == 'login':
            operation_login_user(db, namespace)
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
    ######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            operation_task_add(namespace, current.tasks)
        elif namespace.command == 'remove':
            operation_remove(current.tasks, namespace)
        elif namespace.command == 'show':
            operation_taks_show(current.tasks, namespace)
        elif namespace.command == 'finish':
            operation_task_finish(current.tasks, namespace)
        elif namespace.command == 'move':
            operation_task_move(current.tasks, namespace)
        elif namespace.command == 'change':
            operation_task_change(current.tasks, namespace)
        elif namespace.command == 'share':
            operation_task_share(current.tasks, db, namespace)
    #######################################
    elif namespace.target == 'calendar':
        calendar_custom.print_month_calendar(current.tasks, namespace.date[0], namespace.date[1])
    #######################################
    elif namespace.target == 'user':
        if namespace.command == 'logout':
            operation_logout_user(db)
        elif namespace.command == 'remove':
            operation_remove(db, namespace)
        elif namespace.command == 'info':
            current.print()
    elif namespace.target == 'plan':
        if namespace.command == 'add':
            operation_plan_add(user.plans, namespace)
        elif namespace.command == 'show':
            if namespace.id:
                operation_plan_show_id(user.plans, namespace)
            else:
                operation_plan_show_all(user.plans, namespace)
        elif namespace.command == 'remove':
            operation_plan_remove(user.plans, namespace)
    database.serialize(db, 'database.json')


if __name__ == '__main__':
    main()
