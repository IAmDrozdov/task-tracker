from lib.task import Task
from lib import datetime_parser
import re
from datetime import datetime
import copy


def rec_task_show_all(container, options):
    if container:
        for task in container:
            task.table_print(options.colored)
            rec_task_show_all(task.subtasks, options)


def rec_task_show_id(container, options):
    if container:
        for task in container:
            if task.id == options.choosen:
                task.table_print(options.colored)
                rec_task_show_all(task.subtasks, options)
                return
            rec_task_show_id(task.subtasks, options)


def rec_task_show_tags(container, options):
    if container:
        for task in container:
            if all(elem in task.tags for elem in options.choosen.split()):
                task.table_print(options.colored)
            rec_task_show_tags(task.subtasks, options)


def rec_task_add_sub(container, options):
    if container:
        for task in container:
            if task.id == options.subtask:
                new_task = Task(info=options.description,
                                id=task.id + '_' + Task.get_actual_index(task.subtasks),
                                deadline=datetime_parser.get_deadline(
                                    options.deadline) if options.deadline else None,
                                tags=re.sub("[^\w]", " ",  options.tags).split() if options.tags else [],
                                priority=options.priority if options.priority else 1,
                                indent=task.id.count('_') + 1)
                task.subtasks.append(new_task)
                return
            rec_task_add_sub(task.subtasks, options)


def operation_task_add(options, container):
    if options.subtask:
        rec_task_add_sub(container, options)
    elif options.periodic:
        pass
    else:
        new_task = Task(info=options.description,
                        id=Task.get_actual_index(container, False),
                        deadline=datetime_parser.get_deadline(options.deadline) if options.deadline else None,
                        tags=re.sub("[^\w]", " ",  options.tags).split() if options.tags else [],
                        priority=options.priority if options.priority else 1)
        container.append(new_task)


def operation_task_show(container, options):
    if len(container) == 0:
        print('Nothing to show')
    if options.to_show == 'id':
        rec_task_show_id(container, options)
    elif options.to_show == 'tag':
        rec_task_show_tags(container, options)
    elif options.all:
        rec_task_show_all(container, options)
    else:
        for index, task in enumerate(container):
            task.table_print(options.colored)
            if index == 9:
                return


def rec_task_delete(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                container.remove(task)
                return
            operation_user_remove(task.subtasks, options)


def operation_user_remove(container, options):
    rec_task_delete(container, options)


def rec_task_finish_all(container):
    if container:
        for task in container:
            task.status = 'finished'
            rec_task_finish_all(task.subtasks)


def rec_task_finish(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                task.status = 'finished'
                rec_task_finish_all(task.subtasks)
            rec_task_finish(task.subtasks, options)


def operation_task_finish(container, options):
    rec_task_finish(container, options)


def rec_task_find(container, idx_mass):
    for task in container:
        if int(task.id.split('_')[len(task.id.split('_')) - 1]) == int(idx_mass[0]):
            if len(idx_mass) > 1:
                return rec_task_find(task.subtasks, idx_mass[1:])
            else:
                return task


def rec_task_move_sub(owner):
    if owner.subtasks:
        for task in owner.subtasks:
            task.id = owner.id + '_' + str(int(Task.get_actual_index(owner.subtasks, True)) - 1)
            task.indent = owner.id.count('_') + 1
            rec_task_move_sub(task)


def operation_task_move(container, options):
    task_from = rec_task_find(container, options.id_from.split('_'))
    task_to = rec_task_find(container, options.id_to.split('_'))
    if task_to and task_from:
        task_from.id = task_to.id + '_' + Task.get_actual_index(task_to.subtasks)
        task_from.indent = task_from.id.count('_')
        rec_task_move_sub(task_from)
        temp_task = copy.deepcopy(task_from)
        rec_task_delete(container, task_from)
        task_to.subtasks.append(temp_task)


def rec_task_change(container, options):
    if container:
        for task in container:
            if task.id == options.id:
                if options.deadline:
                    task.deadline = datetime_parser.get_deadline(options.deadline)
                if options.info:
                    task.info = options.info
                if options.priority:
                    task.priority = options.priority
                if options.status:
                    task.status = options.status
                if options.append_tags:
                    for tag in re.sub("[^\w]", " ",  options.append_tags).split():
                        task.tags.append(tag)
                    task.tags = list(set(task.tags))
                if options.remove_tags:
                    for tag in re.sub("[^\w]", " ", options.remove_tags).split():
                        if tag in task.tags:
                            task.tags.remove(tag)
                task.changed = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                return
            rec_task_change(task.subtasks, options)


def operation_task_change(container, options):
    rec_task_change(container, options)


def rec_default_subs(new_task):
    if new_task.subtasks:
        for index, task in enumerate(new_task.subtasks):
            task.id = new_task.id + '_' + str(index + 1)
            task.indent = task.id.count('_')
            rec_default_subs(task)


def operation_task_share(current_user_tasks, container, options):
    task_from = rec_task_find(current_user_tasks, options.id_from.split('_'))
    for user in container['users']:
        if user.nickname == options.nickname_to:
            user_to = user
            break
    else:
        print('Nowhere to send task')
        return
    new_task = copy.deepcopy(task_from)
    new_task.id = Task.get_actual_index(user_to.tasks, False)
    new_task.indent = 0
    rec_default_subs(new_task)
    user_to.tasks.append(new_task)
    if options.delete:
        current_user_tasks.remove(task_from)