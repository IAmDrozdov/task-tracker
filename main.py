#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

from task import Task
from task_container import TaskContainer
import sys


def main():
    container = TaskContainer()
    if sys.argv[1] == 'add':
        container.push(Task(sys.argv[2]))
    pass


if __name__ == '__main__':
    main()
