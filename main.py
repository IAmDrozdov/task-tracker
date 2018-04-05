#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-


import randomizer
import database
import datetime_parser
from parser import create_parser
from task import Task


def main():
    container = database.deserialize('database_tasks.json')
    parser = create_parser()
    namespace = parser.parse_args()
    #################################
    if namespace.command == 'add':
        info_new = namespace.description
        id_new = randomizer.get_actual_index(container)
        if namespace.deadline:
            deadline_new = datetime_parser.get_deadline(namespace.deadline)
        else:
            deadline_new = None
        new_task = Task(info=info_new, id=id_new, deadline=deadline_new)
        container.append(new_task)
        database.serialize(container, 'database_tasks.json')
    #######################################
    elif namespace.command == 'remove':
        Task.delete(container, namespace.id)
    #########################################
    elif namespace.command == "show":
        if namespace.id is not None:
            Task.print(container, namespace.id)
        else:
            Task.print(container)


if __name__ == '__main__':
    main()
