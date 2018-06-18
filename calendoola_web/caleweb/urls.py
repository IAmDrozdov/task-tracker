import django.contrib.auth.views as auth_views
from django.conf.urls import url, include
from django.views.generic import RedirectView

from . import views

task_patterns = [
    url(r'^$', views.TaskListView.as_view(), name='tasks'),
    url(r'^search/$', views.TaskListSearchView.as_view(), name='search-tasks'),
    url(r'^new/$', views.TaskCreateView.as_view(), name='new-task'),
    url(r'^archive/$', views.TaskArchiveListView.as_view(), name='archive'),
    url(r'^(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='task-detail'),
    url(r'^(?P<pk>\d+)/edit/$', views.TaskUpdateView.as_view(), name='edit-task'),
    url(r'^(?P<pk>\d+)/restore/$', views.restore_task, name='restore-task'),
    url(r'^(?P<pk>\d+)/finish/$', views.finish_task, name='finish-task'),
    url(r'^(?P<pk>\d+)/share/$', views.share_task, name='share-task'),
    url(r'^(?P<pk>\d+)/move/$', views.move_task, name='move-task'),
    url(r'^(?P<pk>\d+)/remove/$', views.TaskDeleteView.as_view(), name='remove-task'),
    url(r'^(?P<pk>\d+)/unshare/(?P<name>\w+)/$', views.unshare_task, name='unshare-task'),
]

plan_patterns = [
    url(r'^$', views.PlanListView.as_view(), name='plans'),
    url(r'^new/$', views.PlanCreateView.as_view(), name='new-plan'),
    url(r'^(?P<pk>\d+)/remove/$', views.PlanDeleteView.as_view(), name='remove-plan'),
    url(r'^(?P<pk>\d+)/set-state/$', views.plan_set_state, name='plan-set-state'),
    url(r'^(?P<pk>\d+)/edit/$', views.PlanUpdateView.as_view(), name='edit-plan'),
]

reminder_patterns = [
    url(r'^$', views.ReminderListView.as_view(), name='reminders'),
    url(r'^new/$', views.ReminderCreateView.as_view(), name='new-reminder'),
    url(r'^(?P<pk>\d+)/$', views.ReminderDetailView.as_view(), name='reminder-detail'),
    url(r'^(?P<pk>\d+)/remove/$', views.ReminderDeleteView.as_view(), name='remove-reminder'),
    url(r'^(?P<pk>\d+)/set-state/$', views.reminder_set_state, name='reminder-set-state'),
    url(r'^(?P<pk>\d+)/edit/$', views.ReminderUpdateView.as_view(), name='edit-reminder'),
    url(r'^(?P<pk>\d+)/add-task/$', views.reminder_add_task, name='reminder-add-task'),
    url(r'^(?P<pk>\d+)/detach/(?P<task>\d+)/$', views.reminder_detach_task, name='reminder-detach-task')
]

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='tasks'), name='homepage'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^tasks/', include(task_patterns)),
    url(r'^plans/', include(plan_patterns)),
    url(r'^reminders/', include(reminder_patterns)),
]
