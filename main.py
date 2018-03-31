#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

from task import Task
import json
import sys
from pprint import pprint


def main():
    container = []
    if sys.argv[1] == 'add':
        container.append(Task(sys.argv[2]))
    elif sys.argv[1] == 'remove':
        for task in container:
            if task.name == sys.argv[2]:
                del task
        else:
            print('nothing to delete')
    pprint(container)


if __name__ == '__main__':
    main()
