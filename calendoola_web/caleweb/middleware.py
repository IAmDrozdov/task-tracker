from .views import db


def instances_checker(username):
    for task in db.get_tasks(username):
        overdue = task.check_deadline()
        if overdue:
            task.finish()
            task.pass_to_archive()
    for plan in db.get_plans(username):
        new_plan = plan.check_for_create()
        if new_plan:
            db.add_completed(username, 'plan', new_plan)
    for reminder in db.get_reminders(username):
        reminder.check_tasks()


class InstanceCheckingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.username:
            instances_checker(request.user.username)

        response = self.get_response(request)

        return response
