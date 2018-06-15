import django.contrib.auth.views as auth_views
from django.conf.urls import url

from . import views

urlpatterns = [
    # ####GENERAL####URLS####
    url(r'^$', views.index, name='homepage'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    # ####TASK####URLS####
    url(r'^tasks/$', views.TaskListView.as_view(), name='tasks'),
    url(r'^tasks/search/', views.TaskListSearchView.as_view(), name='search-tasks'),
    url(r'^tasks/archive/$', views.TaskArchiveListView.as_view(), name='archive'),
    url(r'^tasks/(?P<pk>\d+)/$', views.TaskDetailView.as_view(), name='task-details'),
    url(r'^tasks/new/$', views.TaskCreateView.as_view(), name='new-task'),
    url(r'^tasks/(?P<pk>\d+)/edit/$', views.TaskUpdateView.as_view(), name='edit-task'),
    url(r'^tasks/(?P<pk>\d+)/restore/$', views.restore_task, name='restore-task'),
    url(r'^tasks/(?P<pk>\d+)/finish/$', views.finish_task, name='finish-task'),
    url(r'^tasks/(?P<pk>\d+)/share/$', views.share_task, name='share-task'),
    url(r'^tasks/(?P<pk>\d+)/move/$', views.move_task, name='move-task'),
    url(r'^tasks/(?P<pk>\d+)/remove/$', views.TaskDeleteView.as_view(), name='remove-task'),
    url(r'^tasks/(?P<pk>\d+)/unshare/(?P<name>\w+)/$', views.unshare_task, name='unshare-task'),
    # ####PLAN####URLS####
    url(r'^plans/$', views.PlanListView.as_view(), name='plans'),
    url(r'^plans/(?P<pk>\d+)/remove/$', views.PlanDeleteView.as_view(), name='remove-plan'),
    url(r'^plans/(?P<pk>\d+)/set-state', views.plan_set_state, name='plan-set-state'),
    url(r'^plans/new/$', views.PlanCreateView.as_view(), name='new-plan'),
    url(r'^plans/add-plan/$', views.PlanListView.as_view(), name='add-plan'),
    url(r'^plans/(?P<pk>\d+)/edit/$', views.PlanListView.as_view(), name='edit-plan'),
    url(r'^tasks/save-plan/$', views.PlanListView.as_view(), name='save-plan'),
]
