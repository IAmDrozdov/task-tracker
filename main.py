#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

from task import Task
import sys
import json
from datetime import datetime
from parser import Encoder
from randomizer import Randomizer


def main():
    container = json.loads(open('database.json').read())

    if sys.argv[1] == 'add':
        new_task = Task(info=sys.argv[2],
                        id=Randomizer.get_actual_index(container),
                        deadline=datetime.strptime(sys.argv[3] + str(datetime.now().year), '%d %b%Y'))
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
            print('#', index, '|', task['info'], '|', task['id'], '|', task['status'],
                  datetime.strptime(task['date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime('%d.%m.%Y'))


if __name__ == '__main__':
    main()
