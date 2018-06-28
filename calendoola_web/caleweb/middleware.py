from calelib.constants import Notifications
from django.contrib import messages
from .views import db


def instances_checker(username):
    notifications = []
    for task in db.get_tasks(username):
        notifications.append(task.check_deadline())
    for plan in db.get_plans(username):
        new_planned, notification = plan.check_for_create()
        notifications.append(notification)
        if new_planned != Notifications.REMOVED and new_planned is not None:
            db.add_completed(username, 'task', new_planned)
    for reminder in db.get_reminders(username):
        notifications.extend(reminder.check_tasks())
    return filter(None, notifications)


class InstanceCheckingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.username:
            notifications = instances_checker(request.user.username)
            if request.path != '/':
                for n in notifications:
                    if n.title == Notifications.REMOVED or n.title == Notifications.OVERDUE:
                        messages.error(request, f'{n.title} {n.info}')
                    elif n.title == Notifications.PLANNED:
                        messages.info(request, f'{n.title} {n.info}')
                    elif n.title == Notifications.REMIND:
                        messages.warning(request, f'{n.title} {n.info}')

        response = self.get_response(request)
        return response
