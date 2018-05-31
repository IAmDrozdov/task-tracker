from calelib.models import User


class Database:
    def __init__(self):
        self._current_user = None

    current_user = property()

    @current_user.setter
    def current_user(self, nickname):
        self._current_user = User.objects.get(nickname=nickname)

    @current_user.getter
    def current_user(self):
        return self._current_user

    @current_user.deleter
    def current_user(self):
        self._current_user = None

    def get_tasks(self, task_id=None, tags=None):
        if tags:
            return self._current_user.tasks.filter(tags__contains=tags)
        elif task_id:
            return self._current_user.tasks.get(pk=task_id)
        else:
            return self._current_user.tasks.all()

    def remove_task(self, task_id):
        self._current_user.remove_task(task_id)

    def create_task(self, task):
        self._current_user.add_task(task)

    def change_task(self, task_id, info, deadline, priority, status, plus_tags, minus_tags):
        self._current_user.tasks.get(pk=task_id).update(info, deadline, priority, status, plus_tags, minus_tags)

    def get_plans(self, plan_id=None):
        if plan_id:
            return self._current_user.plans.get(pk=plan_id)
        else:
            return self._current_user.plans.all()

    def create_plan(self, plan):
        self._current_user.add_plan(plan)

    def remove_plan(self, plan_id):
        self._current_user.remove_plan(plan_id)

    @staticmethod
    def create_user(nickname):
        User.objects.create(nickname=nickname)

    @staticmethod
    def remove_user(nickname):
        User.objects.get(nickname=nickname).delete()
