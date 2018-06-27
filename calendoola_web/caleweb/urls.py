import django.contrib.auth.views as auth_views
from django.conf.urls import (
    url,
    include,
)
from django.views.generic import RedirectView

from . import views

task_patterns = [
    url(r'^$', views.TaskListView.as_view(), name='all'),
    url(r'^search/$', views.TaskListSearchView.as_view(), name='search'),
    url(r'^new/$', views.TaskCreateView.as_view(), name='new'),
    url(r'^archive/$', views.TaskArchiveListView.as_view(), name='archive'),
    url(r'^(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/edit/$', views.TaskUpdateView.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/restore/$', views.restore_task, name='restore'),
    url(r'^(?P<pk>\d+)/finish/$', views.finish_task, name='finish'),
    url(r'^(?P<pk>\d+)/share/$', views.share_task, name='share'),
    url(r'^(?P<pk>\d+)/move/$', views.move_task, name='move'),
    url(r'^(?P<pk>\d+)/remove/$', views.TaskDeleteView.as_view(), name='remove'),
    url(r'^(?P<pk>\d+)/unshare/(?P<name>\w+)/$', views.unshare_task, name='unshare'),
    url(r'^(?P<pk>\d+)/add-subtask', views.AddSubtaskView.as_view(), name='add-subtask')
]

plan_patterns = [
    url(r'^$', views.PlanListView.as_view(), name='all'),
    url(r'^new/$', views.PlanCreateView.as_view(), name='new'),
    url(r'^(?P<pk>\d+)/remove/$', views.PlanDeleteView.as_view(), name='remove'),
    url(r'^(?P<pk>\d+)/set-state/$', views.plan_set_state, name='set-state'),
    url(r'^(?P<pk>\d+)/edit/$', views.PlanUpdateView.as_view(), name='edit'),
]

reminder_patterns = [
    url(r'^$', views.ReminderListView.as_view(), name='all'),
    url(r'^new/$', views.ReminderCreateView.as_view(), name='new'),
    url(r'^(?P<pk>\d+)/$', views.ReminderDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/remove/$', views.ReminderDeleteView.as_view(), name='remove'),
    url(r'^(?P<pk>\d+)/set-state/$', views.reminder_set_state, name='set-state'),
    url(r'^(?P<pk>\d+)/edit/$', views.ReminderUpdateView.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/add-task/$', views.reminder_add_task, name='add-task'),
    url(r'^(?P<pk>\d+)/detach/(?P<task>\d+)/$', views.reminder_detach_task, name='detach-task')
]

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='tasks'), name='homepage'),
    url(r'^login/$', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^tasks/', include(task_patterns, namespace='tasks')),
    url(r'^plans/', include(plan_patterns, namespace='plans')),
    url(r'^reminders/', include(reminder_patterns, namespace='reminders')),
]
