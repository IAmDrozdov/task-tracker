from .views import db
from django.http import Http404
from django.urls.exceptions import NoReverseMatch

def instances_checker(username):
    for task in db.get_tasks(username, ):
        overdue = task.check_deadline()
        if overdue:
            task.finish()
            task.pass_to_archive()
    for plan in db.get_plans(username):
        new_planned = plan.check_for_create()
        if new_planned:
            db.add_completed(username, 'task', new_planned)
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
