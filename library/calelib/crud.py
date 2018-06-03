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

    def get_tasks(self, task_id=None, tags=None, archive=False):
        if tags:
            return self._current_user.tasks.filter(tags__contains=tags)
        elif task_id:
            return self._current_user.search_task(task_id)
        elif archive:
            return self._current_user.tasks.filter(archived=True)
        else:
            return self._current_user.tasks.filter(archived=False)

    def remove_task(self, task_id):
        self._current_user.remove_task(task_id)

    def create_task(self, task):
        self._current_user.add_task(task)

    def change_task(self, task_id, info, deadline, priority, status, plus_tags, minus_tags):
        self._current_user.search_task(task_id).update(info, deadline, priority, status, plus_tags, minus_tags)

    def get_plans(self, plan_id=None):
        return self._current_user.plans.get(pk=plan_id) if plan_id else self._current_user.plans.all()

    def create_plan(self, plan):
        self._current_user.add_plan(plan)

    def remove_plan(self, plan_id):
        self._current_user.remove_plan(plan_id)

    def change_plan(self, plan_id, info, period_type, period_value, time):
        self._current_user.plans.get(pk=plan_id).update(info, period_type, period_value, time)

    @staticmethod
    def create_user(nickname):
        User.objects.create(nickname=nickname)

    @staticmethod
    def remove_user(nickname):
        User.objects.get(nickname=nickname).delete()

    @staticmethod
    def get_users(user_nickname):
        return User.objects.get(nickname=user_nickname) if user_nickname else User.objects.all()
