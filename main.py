#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

from task import Task
import sys
import json
from parser import Encoder


def get_actual_index(container):
    if len(container) == 0:
        return 1
    else:
        return container[len(container)-1]['id'] + 1


def main():
    container = json.loads(open('database.json').read())

    if sys.argv[1] == 'add':
        new_task = Task(info=sys.argv[2], id=get_actual_index(container))
        container.append(new_task)

        with open('database.json', mode='w', encoding='utf-8') as db:
            json.dump(container, db, cls=Encoder, indent=4)

    elif sys.argv[1] == 'remove':
        for task in container:
            if task['id'] == int(sys.argv[2]):
                container.remove(task)
                with open('database.json', mode='w', encoding='utf-8') as db:
                    json.dump(container, db, cls=Encoder, indent=4)
                break
        else:
            print('nothing to delete')
    elif sys.argv[1] == "show":
        for index, task in enumerate(container):
            print('#', index, '|', task['info'], '|', task['id'], '|', task['date'])


if __name__ == '__main__':
    main()
