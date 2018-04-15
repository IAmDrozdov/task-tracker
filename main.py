#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from lib import database, datetime_parser, calendar_custom
from parser import create_parser
from lib.task import Task


def rec_show_all(container, is_colored=False):
    if container:
        for task in container:
            task.table_print(is_colored)
            rec_show_all(task.subtasks, is_colored)


def rec_show_id(container, id, is_colored=False):
    if container:
        for task in container:
            if task.id == id:
                task.table_print(is_colored)
                rec_show_all(task.subtasks, is_colored)
            rec_show_id(task.subtasks, id, is_colored)


def rec_show_tags(container, tags, is_colored=False):
    if container:
        for task in container:
            if all(elem in task.tags for elem in tags):
                task.table_print(is_colored)
            rec_show_tags(task.subtasks, tags, is_colored)


def rec_add_sub(container, options):
    if container:
        for task in container:
            if task.id == options.subtask:
                new_task = Task(info=options.description,
                                id=task.id + '_' + Task.get_actual_index(task.subtasks),
                                deadline=datetime_parser.get_deadline(
                                    options.deadline) if options.deadline else None,
                                tags=options.tags.split() if options.tags else [],
                                priority=options.priority if options.priority else 1,
                                indent=task.id.count('_') + 1)
                task.subtasks.append(new_task)
                return
            rec_add_sub(task.subtasks, options)


def operation_add(options, container):
    if options.subtask:
        rec_add_sub(container, options)
    else:
        new_task = Task(info=options.description,
                        id=Task.get_actual_index(container, False),
                        deadline=datetime_parser.get_deadline(options.deadline) if options.deadline else None,
                        tags=options.tags.split() if options.tags else [],
                        priority=options.priority if options.priority else 1)
        container.append(new_task)
    database.serialize(container, 'database_tasks.json')


def operation__show(container, options):
    if len(container) == 0:
        print('Nothing to show')
    if options.to_show == 'id':
        rec_show_id(container, options.choosen, options.colored)
    elif options.to_show == 'tag':
        rec_show_tags(container, options.choosen.split(), options.colored)
    elif options.to_show == 'all' or options.to_show is None:
        rec_show_all(container, options.colored)


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


def main():
    container = database.deserialize('database_tasks.json')
    parser = create_parser()
    namespace = parser.parse_args()
    ######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            operation_add(namespace, container)
    #######################################
        elif namespace.command == 'remove':
            operation_remove(container, namespace)
    #######################################
        elif namespace.command == 'show':
            operation__show(container, namespace)
        elif namespace.command == 'finish':
            operation_finish(container, namespace)
    #######################################
    elif namespace.target == 'calendar':
        calendar_custom.print_month_calendar(container, namespace.date[0], namespace.date[1])


if __name__ == '__main__':
    main()
