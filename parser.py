import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    subparser_targets = parser.add_subparsers(dest='target')

    targets_task = subparser_targets.add_parser('task', help='Working with tasks')
    task_parser = targets_task.add_subparsers(dest='command')

    add_task = task_parser.add_parser('add', help='Add new task')
    add_task.add_argument('description', help='Information what task should hold')
    add_task.add_argument('-dl', '--deadline', help='Attach deadline for task')
    add_task.add_argument('-t', '--tags', help='Attach tags for task')
    add_task.add_argument('-p', '--priority', type=int, help='Attach priority for task, default is 1')
    add_task.add_argument('-s', '--subtask', type=str, help='ID of task for what you want to add new '
                                                            'task as subtask')
    add_task.add_argument('-pt', '--periodic', action='store_true', help='Make task periodic')
    add_task.add_argument('-wd', '--weekdays', help='Repeat very entered')
    add_task.add_argument('-d', '--days', help='Repeat every entered N days')
    add_task.add_argument('-r', '--remind', help='Create task at certain time. Or default will be 00:00')

    show_task = task_parser.add_parser('show', help='SHow full information about task')
    show_task.add_argument('to_show', action='store', nargs='?', choices=('all', 'id', 'tags'), help='Filter for show')
    show_task.add_argument('choosen', nargs='?', help='value of choosen filter')
    show_task.add_argument('-c', '--colored', action='store_true', help='If true priority of task will influence on '
                                                                        'color')

    remove_task = task_parser.add_parser('remove', help='Remove task by ID. If task has subtasks, they will be removed'
                                                        ' too')
    remove_task.add_argument('id', type=str, help='ID of task what should delete')

    change_task = task_parser.add_parser('finish', help='Change status of task to finish. If task has subtasks, they '
                                                        'wil be finished too')
    change_task.add_argument('id', type=str, help='ID of task to finish to finish')

    move_task = task_parser.add_parser('move', help='Make the first task a subtask the second task')
    move_task.add_argument('id_from', type=str, help='ID of task which will be subtask')
    move_task.add_argument('id_to', type=str, help='ID of parent task')

    targets_calendar = subparser_targets.add_parser('calendar', help='Working with calendar')
    calendar_parser = targets_calendar.add_subparsers(dest='command')

    show_calendar = calendar_parser.add_parser('show', help='Show any month with colored deadlines')
    show_calendar.add_argument('date', type=int, nargs=2, help='Month and year of date to show')
    return parser
