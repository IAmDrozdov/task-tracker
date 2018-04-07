#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


import randomizer
import database
import datetime_parser
from parser import create_parser
from task import Task
import calendar_custom


def main():
    container = database.deserialize('database_tasks.json')
    parser = create_parser()
    namespace = parser.parse_args()
    ######################################
    if namespace.target == 'task':
        if namespace.command == 'add':
            if namespace.subtask:
                for task in container:
                    if task['id'] == namespace.subtask:
                        info_new = namespace.description
                        id_new = task['id'] + '_' + randomizer.get_actual_index(task['subtasks'])
                        deadline_new = datetime_parser.get_deadline(namespace.deadline) if namespace.deadline else None
                        tags_new = namespace.tags.split() if namespace.tags else []
                        priority_new = int(namespace.priority) if namespace.priority else 1
                        indent_new = task['indent'] + 1
                        new_task = Task(info=info_new, id=id_new, deadline=deadline_new, tags=tags_new,
                                        priority=priority_new, indent=indent_new)
                        Task.add_subtask(task, new_task)
                        database.serialize(container, 'database_tasks.json')
                        break
                else:
                    print('nowhere to append')
            else:
                info_new = namespace.description
                id_new = randomizer.get_actual_index(container, False)
                deadline_new = datetime_parser.get_deadline(namespace.deadline) if namespace.deadline else None
                tags_new = namespace.tags.split() if namespace.tags else []
                priority_new = int(namespace.priority) if namespace.priority else 1
                new_task = Task(info=info_new, id=id_new, deadline=deadline_new, tags=tags_new, priority=priority_new)
                container.append(new_task)
                database.serialize(container, 'database_tasks.json')
    #######################################
        elif namespace.command == 'remove':
            Task.delete(container, namespace.id)
    #######################################
        elif namespace.command == 'show':
            if namespace.to_show == 'id':
                Task.print(container, namespace.choosen)
            elif namespace.to_show == 'tag':
                Task.print(container, tag=namespace.choosen)
            elif namespace.to_show == 'all' or namespace.to_show is None:
                Task.print(container)
        elif namespace.command == 'finish':
            for task in container:
                if task['id'] == namespace.id:
                    Task.change_status(task)
                    database.serialize(container, 'database_tasks.json')
    #######################################
    elif namespace.target == 'calendar':
        calendar_custom.print_month_calendar(container, namespace.date[0], namespace.date[1])


if __name__ == '__main__':
    main()
