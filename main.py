#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from lib import database, datetime_parser, calendar_custom
from parser import create_parser
from lib.task import Task
import re
import copy


def rec_show_all(container, options):
    if container:
        for task in container:
            task.table_print(options.colored)
            rec_show_all(task.subtasks, options)


def rec_show_id(container, options):
    if container:
        for task in container:
            if task.id == options.choosen:
                task.table_print(options.colored)
                rec_show_all(task.subtasks, options)
                return
            rec_show_id(task.subtasks, options)


def rec_show_tags(container, options):
    if container:
        for task in container:
            if all(elem in task.tags for elem in options.choosen.split()):
                task.table_print(options.colored)
            rec_show_tags(task.subtasks, options)


def rec_add_sub(container, options):
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
            rec_add_sub(task.subtasks, options)


def operation_add(options, container):
    if options.subtask:
        rec_add_sub(container, options)
    elif options.periodic:
        pass
    else:
        new_task = Task(info=options.description,
                        id=Task.get_actual_index(container, False),
                        deadline=datetime_parser.get_deadline(options.deadline) if options.deadline else None,
                        tags=re.sub("[^\w]", " ",  options.tags).split() if options.tags else [],
                        priority=options.priority if options.priority else 1)
        container.append(new_task)
    database.serialize(container, 'database_tasks.json')


def operation__show(container, options):
    if len(container) == 0:
        print('Nothing to show')
    if options.to_show == 'id':
        rec_show_id(container, options)
    elif options.to_show == 'tag':
        rec_show_tags(container, options)
    elif options.all:
        rec_show_all(container, options)
    else:
        for index, task in enumerate(container):
            task.table_print(options.colored)
            if index == 9:
                return


def rec_delete(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                container.remove(task)
                return
            operation_remove(task.subtasks, options)


def operation_remove(container, options):
    rec_delete(container, options)
    database.serialize(container, 'database_tasks.json')


def rec_finish_all(container):
    if container:
        for task in container:
            task.status = 'finished'
            rec_finish_all(task.subtasks)


def rec_finish(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                task.status = 'finished'
                rec_finish_all(task.subtasks)
            rec_finish(task.subtasks, options)


def operation_finish(container, options):
    rec_finish(container, options)
    database.serialize(container, 'database_tasks.json')


def rec_find(container, idx_mass):
    for task in container:
        if int(task.id.split('_')[len(task.id.split('_')) - 1]) == int(idx_mass[0]):
            if len(idx_mass) > 1:
                return rec_find(task.subtasks, idx_mass[1:])
            else:
                return task


def rec_move_sub(owner):
    if owner.subtasks:
        for task in owner.subtasks:
            task.id = owner.id + '_' + str(int(Task.get_actual_index(owner.subtasks, True)) - 1)
            task.indent = owner.id.count('_') + 1
            rec_move_sub(task)


def operation_move(container, options):
    mapping = options.id_from.split('_')
    task_from = rec_find(container, mapping)
    mapping = options.id_to.split('_')
    task_to = rec_find(container, mapping)
    if task_to and task_from:
        task_from.id = task_to.id + '_' + Task.get_actual_index(task_to.subtasks)
        task_from.indent = task_from.id.count('_')
        rec_move_sub(task_from)
        temp_task = copy.deepcopy(task_from)
        rec_delete(container, task_from)
        task_to.subtasks.append(temp_task)
        database.serialize(container, 'database_tasks.json')


def rec_change(container, options):
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
                return
            rec_change(task.subtasks, options)


def operation_change(container, options):
    rec_change(container, options)
    database.serialize(container, 'database_tasks.json')


def main():
    container = database.deserialize('database_tasks.json')
    parser = create_parser()
    namespace = parser.parse_args()
    ######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            operation_add(namespace, container)
        elif namespace.command == 'remove':
            operation_remove(container, namespace)
        elif namespace.command == 'show':
            operation__show(container, namespace)
        elif namespace.command == 'finish':
            operation_finish(container, namespace)
        elif namespace.command == 'move':
            operation_move(container, namespace)
        elif namespace.command == 'change':
            operation_change(container, namespace)
    #######################################
    elif namespace.target == 'calendar':
        calendar_custom.print_month_calendar(container, namespace.date[0], namespace.date[1])
    #######################################
    elif namespace.target == 'user':
        print(namespace)
        if namespace.command == 'login':
            pass
        elif namespace.command == 'logout':
            pass
        elif namespace.command == 'create':
            pass
        elif namespace.command == 'remove':
            pass
        elif namespace.command == 'info':
            pass


if __name__ == '__main__':
    main()
