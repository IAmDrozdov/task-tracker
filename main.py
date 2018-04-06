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
            info_new = namespace.description
            id_new = randomizer.get_actual_index(container)
            deadline_new = datetime_parser.get_deadline(namespace.deadline) if namespace.deadline else None
            tags_new = namespace.tags.split() if namespace.tags else []
            new_task = Task(info=info_new, id=id_new, deadline=deadline_new, tags=tags_new)
            container.append(new_task)
            database.serialize(container, 'database_tasks.json')
        #######################################
        elif namespace.command == 'remove':
            Task.delete(container, namespace.id)
        #######################################
        elif namespace.command == 'show':
            if namespace.id is not None:
                Task.print(container, namespace.id)
            else:
                Task.print(container)
    #######################################
    elif namespace.target == 'calendar':
        calendar_custom.print_month_calendar(container, namespace.date[0], namespace.date[1])


if __name__ == '__main__':
    main()
