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
    add_task.add_argument('-p', '--priority', type=int, choices=[1, 2, 3, 4, 5],
                          help='Attach priority for task, default is 1')
    add_task.add_argument('-s', '--subtask', type=str, help='ID of task for what you want to add new '
                                                            + 'task as subtask')

    show_task = task_parser.add_parser('show', help='Print full information about task')
    show_task.add_argument('to_show', action='store', nargs='?', choices=('id', 'tags', 'archive'),
                           help='Filter for show')
    show_task.add_argument('selected', nargs='?', help='Value of choosen filter or ID')
    show_task.add_argument('-c', '--colored', action='store_true', help='If true priority of task will influence on '
                                                                        + 'color')

    remove_task = task_parser.add_parser('remove', help='Remove task by ID. If task has subtasks, they will be removed'
                                                        + ' too')
    remove_task.add_argument('id', type=int, help='ID of task what should delete')

    finish_task = task_parser.add_parser('finish', help='Change status of task to finish. If task has subtasks, they '
                                                        + 'wil be finished too')
    finish_task.add_argument('id', type=int, help='ID of task to finish to finish')

    move_task = task_parser.add_parser('move', help='Make the first task a subtask the second task')
    move_task.add_argument('id_from', type=int, help='ID of task which will be subtask')
    move_task.add_argument('id_to', type=int, help='ID of parent task')

    change_task = task_parser.add_parser('change', help='Change properties of choosen task')
    change_task.add_argument('id', type=int, help='ID of task to change')
    change_task.add_argument('-dl', '--deadline', help='Change task deadline')
    change_task.add_argument('-i', '--info', help='Change task description')
    change_task.add_argument('-p', '--priority', type=int, help='Change task priority')
    change_task.add_argument('-at', '--append_tags', help='Append new tags for task')
    change_task.add_argument('-rt', '--remove_tags', help='Remove tags from task')
    change_task.add_argument('-s', '--status', help='Change task status')

    share_task = task_parser.add_parser('share', help='Send task to another user')
    share_task.add_argument('id_from', help='ID task what will be send')
    share_task.add_argument('nickname_to', help='Nickname user what will take task')
    share_task.add_argument('-d', '--delete', action='store_true', help='Deleting task from the sender')

    restore_task = task_parser.add_parser('restore', help='Restore task from archive')
    restore_task.add_argument('id', type=int, help='ID of task to restore')

    unshare_task = task_parser.add_parser('unshare', help='Unshare task by id')
    unshare_task.add_argument('id', type=int, help='Task to unshare')

    targets_calendar = subparser_targets.add_parser('calendar', help='Working with calendar')
    calendar_parser = targets_calendar.add_subparsers(dest='command')

    show_calendar = calendar_parser.add_parser('show', help='Show any month with colored deadlines')
    show_calendar.add_argument('date', type=int, nargs=2, help='Month and year of date to show')

    targets_user = subparser_targets.add_parser('user', help='Working with user')
    user_parser = targets_user.add_subparsers(dest='command')

    login_user = user_parser.add_parser('login', help='User authentication')
    login_user.add_argument('nickname', type=str, help='User nickname')

    user_parser.add_parser('logout', help='User deauthentication')

    create_user = user_parser.add_parser('add', help='Create new user')
    create_user.add_argument('nickname', type=str, help='User nickname for authentication')
    create_user.add_argument('-f', '--force', action='store_true', help='After creating user sign in')

    delete_user = user_parser.add_parser('remove', help='Remove user by nickname')
    delete_user.add_argument('nickname', help='User nickname')

    user_parser.add_parser('info', help='Print short information about user')

    targets_plan = subparser_targets.add_parser('plan', help='Working with periodic tasks')
    plan_parser = targets_plan.add_subparsers(dest='command')

    add_plan = plan_parser.add_parser('add', help='Create plan, what will create periodic')
    add_plan.add_argument('description', help='Information for task')
    add_plan.add_argument('period_type', type=str, choices=('day', 'week', 'month', 'year'), help='Type of repeating'
                                                                                                  + 'plan creation.')
    add_plan.add_argument('period_value', type=str, help='Periodic of creating task')
    add_plan.add_argument('-t', '--time', type=str, help='Time when task will be created')

    show_plan = plan_parser.add_parser('show', help='Print list of plans')
    show_plan.add_argument('id', type=str, nargs='?', help='ID of plan to show')
    show_plan.add_argument('-c', '--colored', action='store_true', help='Mark worked plans with another color')

    remove_plan = plan_parser.add_parser('remove', help='Remove plan')
    remove_plan.add_argument('id', type=str, help='ID of plan to delete')

    change_plan = plan_parser.add_parser('change', help='Change plan')
    change_plan.add_argument('id', type=str, help='ID of plan to change')
    change_plan.add_argument('-i', '--info', help='Change information about plan')
    change_plan.add_argument('-pt', '--period_type', type=str, choices=('day', 'week', 'month', 'year'),
                             help='Change period type')
    change_plan.add_argument('-pv', '--period_value', type=str, help='Periodic of creating task')
    change_plan.add_argument('-t', '--time', type=str, help='Time when task will be created')

    target_reminder = subparser_targets.add_parser('reminder', help='Instance that remind before task deadline')
    reminder_parser = target_reminder.add_subparsers(dest='command')

    add_reminder = reminder_parser.add_parser('add', help='Create new reminder')
    add_reminder.add_argument('remind_type', choices=('min', 'hour', 'day', 'month'), help='Type of reminding measure')
    add_reminder.add_argument('remind_value', type=int, help='Number of typed measure')

    remove_reminder = reminder_parser.add_parser('remove', help='Remove reminder')
    remove_reminder.add_argument('id', type=int, help='ID of reminder to remove')

    apply_task = reminder_parser.add_parser('apply', help='Add task to reminder')
    apply_task.add_argument('reminder_id', type=int, help='ID of reminder')
    apply_task.add_argument('task_id', type=int, help='ID of task to append to reminder')

    remove_task_from = reminder_parser.add_parser('detach', help='Remove task from reminder')
    remove_task_from.add_argument('reminder_id', type=int, help='Id of reminder')
    remove_task_from.add_argument('task_id', type=int, help='ID of task to remove')

    show_reminder = reminder_parser.add_parser('show', help='Print information about reminder')
    show_reminder.add_argument('id', type=int, nargs='?', help='ID of reminder, if None print all reminders')

    change_reminder = reminder_parser.add_parser('change', help='Change information about reminder')
    change_reminder.add_argument('id', type=int, help='ID of reminder to change')

    change_reminder.add_argument('remind_type', nargs='?', choices=('min', 'hour', 'day', 'month'),
                                 help='Type of reminding measure')
    change_reminder.add_argument('remind_value', nargs='?', type=int, help='Number of typed measure')
    return parser
