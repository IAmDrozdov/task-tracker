import django.contrib.auth.views as auth_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='homepage'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^tasks/$', views.TaskListView.as_view(), name='tasks'),
    url(r'^tasks/archive/$', views.TaskArchiveListView.as_view(), name='archive'),
    url(r'^plans/$', views.PlanListView.as_view(), name='plans'),
    url(r'^tasks/(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='task-detail'),
    url(r'^plans/(?P<pk>\d+)/$', views.PlanDetailView.as_view(), name='plan'),
    url(r'^tasks/new/$', views.TaskCreateView.as_view(), name='new-task'),
    url(r'^tasks/(?P<pk>\d+)/unfinish/$', views.unfinish_task, name='unfinish_task'),
    url(r'^tasks/(?P<pk>\d+)/finish/$', views.finish_task, name='finish_task'),
    url(r'^tasks/(?P<pk>\d+)/share/$', views.share_task, name='share_task'),
    url(r'^tasks/(?P<pk>\d+)/move/$', views.move_task, name='move_task'),
    url(r'^tasks/remove/(?P<pk>\d+)/$', views.TaskDeleteView.as_view(), name='remove_task'),
    url(r'^plans/remove/(?P<pk>\d+)/$', views.remove_plan, name='remove_plan'),

    url(r'^plans/new/$', views.create_plan, name='new-plan'),
    url(r'^plans/add-plan/$', views.add_plan, name='add_plan'),

    url(r'^tasks/(?P<pk>\d+)/edit/$', views.TaskUpdateView.as_view(), name='edit_task'),
    url(r'^plans/(?P<pk>\d+)/edit/$', views.edit_plan, name='edit_plan'),
    url(r'^tasks/save-plan/$', views.save_plan, name='save_plan'),
]
