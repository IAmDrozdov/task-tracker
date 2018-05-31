from calelib.models import User


class Database:
    def __init__(self, nickname):
        self.current_user = User.objects.get(nickname=nickname)

    def get_tasks(self, task_id, tags=None):
        if tags:
            return self.current_user.tasks.filter(tags__contains=tags)
        elif task_id:
            return self.current_user.tasks.get(pk=task_id)
        else:
            return self.current_user.tasks.all()

    def remove_task(self, task_id):
        self.current_user.remove_task(task_id)

    def create_task(self, task):
        self.current_user.add_task(task)

    def change_task(self, task_id, info, deadline, priority, status, plus_tags, minus_tags):
        self.current_user.tasks.get(pk=task_id).update(info, deadline, priority, status, plus_tags, minus_tags)

    def get_plans(self, plan_id):
        if plan_id:
            return self.current_user.plans.get(pk=plan_id)
        else:
            return self.current_user.plans.all()

    def create_plan(self, plan):
        self.current_user.add_plan(plan)

    def remove_plan(self, plan_id):
        self.current_user.remove_plan(plan_id)
