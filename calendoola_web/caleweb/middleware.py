from calelib.constants import Notifications
from calelib.notification import Notification
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
    return list(filter(None, notifications))


class InstanceCheckingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.username:
            username = request.user.username
            user = db.get_users(username)
            notifications = []
            for tid in user.new_tasks:
                task = db.get_tasks(username=username, task_id=tid)
                notifications.append(Notification(
                    title=f'{username.capitalize()}',
                    info=f'shared you task {task.info}'
                ))
            user.clear_new_tasks()
            notifications.extend(instances_checker(username))
            if request.path != '/':
                for n in notifications:
                    if n.title == Notifications.REMOVED or n.title == Notifications.OVERDUE:
                        messages.error(request, f'{n.title} {n.info}')
                    elif n.title == Notifications.PLANNED:
                        messages.info(request, f'{n.title} {n.info}')
                    else:
                        messages.warning(request, f'{n.title} {n.info}')

        response = self.get_response(request)
        return response

    def process_exceptions(self, request, exception):
        pass
