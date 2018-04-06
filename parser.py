import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    subparser_targets = parser.add_subparsers(dest='target')

    targets_task = subparser_targets.add_parser('task')
    task_parser = targets_task.add_subparsers(dest='command')

    add_task = task_parser.add_parser('add')
    add_task.add_argument('description')
    add_task.add_argument('-dl', '--deadline')
    add_task.add_argument('-t', '--tags')
    add_task.add_argument('-p', '--priority')

    show_task = task_parser.add_parser('show')
    show_task.add_argument('to_show', action='store', nargs='?', choices=('all', 'id', 'tag'))
    show_task.add_argument('choosen', nargs='?')

    remove_task = task_parser.add_parser('remove')
    remove_task.add_argument('id', type=int)

    change_task = task_parser.add_parser('finish')
    change_task.add_argument('id', type=int)

    targets_calendar = subparser_targets.add_parser('calendar')
    calendar_parser = targets_calendar.add_subparsers(dest='command')

    show_calendar = calendar_parser.add_parser('show')
    show_calendar.add_argument('date', type=int, nargs=2)
    return parser
