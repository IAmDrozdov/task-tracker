from lib import datetime_parser
from lib.plan import Plan


def operation_plan_show_all(container, options):
    if len(container) != 0:
        for plan in container:
            plan.colored_print(options.colored)
    else:
        print('No plans')


def operation_plan_show_id(container, options):
    for plan in container:
        if plan.id == options.id:
            print(plan)
            return
    else:
        print('Nothing to show')


def operation_plan_remove(container, options):
    for task in container.tasks:
        if task.plan == options.id:
            container.tasks.remove(task)
    for plan in container.plans:
        if plan.id == options.id:
            container.plans.remove(plan)
            return
    else:
        print('Nothing to delete.')


def operation_plan_add(container, options):
    period_options = datetime_parser.parse_period(options.period)
    p_time = datetime_parser.parse_time(options.time) if options.time else None
    new_plan = Plan(info=options.description, id=Plan.get_actual_index(container),
                    period=period_options[0], period_type=period_options[1], time_in=p_time)
    container.append(new_plan)