#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

from task import Task
import sys
import json
from datetime import datetime
from edcoder import Encoder
from randomizer import Randomizer
from parser import create_parser


def main():
    container = json.loads(open('database.json').read())
    parser = create_parser()
    namespace = parser.parse_args()
    #################################
    if namespace.command == 'add':
        info_new = namespace.description
        id_new = Randomizer.get_actual_index(container)
        if namespace.deadline:
            deadline_new = datetime.strptime(namespace.deadline + str(datetime.now().year), '%d %b%Y')
        else:
            deadline_new = None
        new_task = Task(info=info_new, id=id_new, deadline=deadline_new)
        container.append(new_task)
        with open('database.json', mode='w', encoding='utf-8') as db:
            json.dump(container, db, cls=Encoder, indent=4)
    #######################################
    elif sys.argv[1] == 'remove':
        for task in container:
            if task['id'] == int(sys.argv[2]):
                container.remove(task)
                with open('database.json', mode='w', encoding='utf-8') as db:
                    json.dump(container, db, cls=Encoder, indent=4)
                break
        else:
            print('nothing to delete')
    #########################################
    elif namespace.command == "show":
        if namespace.all:
            for index, task in enumerate(container):
                date_print = datetime.strptime(task['date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%d.%m.%Y')
                if task['deadline'] is None:
                    deadline_print = 'no deadline'
                else:
                    deadline_print = datetime.strptime(task['deadline'], "%Y-%m-%dT%H:%M:%SZ").strftime('%d.%m.%Y')
                print('#', index+1, '|', task['info'], '|', task['id'], '|', task['status'], '|', date_print
                      , '|', deadline_print)
        else:
            for index, task in enumerate(container):
                if task['id'] == namespace.id:
                    date_print = datetime.strptime(task['date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%d.%m.%Y')
                    if task['deadline'] is None:
                        deadline_print = 'no deadline'
                    else:
                        deadline_print = datetime.strptime(task['deadline'], "%Y-%m-%dT%H:%M:%SZ").strftime('%d.%m.%Y')
                    print('#', index+1, '|', task['info'], '|', task['id'], '|', task['status'], '|', date_print
                          , '|', deadline_print)
                    break
            else:
                print('Nothing to show')


if __name__ == '__main__':
    main()
