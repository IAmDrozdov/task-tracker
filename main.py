#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


from lib import database, datetime_parser, calendar_custom
from parser import create_parser
from lib.task import Task
from lib.task_container import TaskContainer


def add_task(task):
    pass


def show_task(task):
    pass


def rec_do(container, func):
    if container:
        for task in container:
            func(task)
            rec_do(task, func)


def rec_show(container):
    for task in container:
        Task.print(container)
        rec_show(task.subtasks)


def rec_search(container, options):
    print(container)
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
            rec_search(task.subtasks, options)


def operation_add(options, container):
    if options.subtask:
        rec_search(container, options)
    else:
        new_task = Task(info=options.description,
                        id=Task.get_actual_index(container, False),
                        deadline=datetime_parser.get_deadline(options.deadline) if options.deadline else None,
                        tags=options.tags.split() if options.tags else [],
                        priority=options.priority if options.priority else 1)
        container.append(new_task)
    database.serialize(container, 'database_tasks.json')


def operation__show(options, container):
    if options.to_show == 'id':
        Task.print(container, options.choosen)
    elif options.to_show == 'tag':
        Task.print(container, tag=options.choosen)
    elif options.to_show == 'all' or options.to_show is None:
        if options.colored:
            Task.print(container, is_colored=True)
        else:
            #Task.print(container)
            rec_show(container)


def operation_remove(container, options):
    if container:
        for task in container:
            Task.delete(container, options.id)


def operation_finish(options, container):
    for task in container:
        if task.id == options.id:
            task.change_status()
            database.serialize(container, 'database_tasks.json')


def main():
    container = TaskContainer()
    parser = create_parser()
    namespace = parser.parse_args()
    ######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            operation_add(namespace, container.list)
    #######################################
        elif namespace.command == 'remove':
            Task.delete(container.list, namespace.id)
    #######################################
        elif namespace.command == 'show':
            operation__show(namespace, container.list)
        elif namespace.command == 'finish':
            operation_finish(namespace, container.list)
    #######################################
    elif namespace.target == 'calendar':
        calendar_custom.print_month_calendar(container.list, namespace.date[0], namespace.date[1])


if __name__ == '__main__':
    main()
