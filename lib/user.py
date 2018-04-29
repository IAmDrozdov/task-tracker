class User:
    def __init__(self, nickname=None):
        self.nickname = nickname
        self.tasks = []
        self.plans = []
        self.archive = []

    def print(self):
        tasks_print = []
        plans_print = []
        if self.tasks:
            for task in self.tasks:
                tasks_print.append(task.info)
            tasks_print = 'tasks:\n' + ', '.join(tasks_print)
        else:
            tasks_print = 'No tasks'

        if self.plans:
            for plan in self.plans:
                plans_print.append(plan.info)
            plans_print = 'plans:\n' + ', '.join(plans_print)
        else:
            plans_print = 'No plans'
        print('user: {}\n{}\n{}'.format(self.nickname, tasks_print, plans_print))
