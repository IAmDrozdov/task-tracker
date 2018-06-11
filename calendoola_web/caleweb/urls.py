from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='homepage'),
    url(r'^tasks/$', views.tasks, name='tasks'),
    url(r'^plans/$', views.plans, name='plans'),
    url(r'^tasks/(?P<pk>\d+)/$', views.task_detail, name='task'),
    url(r'^plans/(?P<pk>\d+)/$', views.plan_detail, name='plan'),
    url(r'^tasks/new/$', views.new_task, name='new_task'),
    url(r'^tasks/(?P<pk>\d+)/unfinish-task$', views.unfinish_task, name='unfinish_task'),
    url(r'^tasks/(?P<pk>\d+)/finish-task$', views.finish_task, name='finish_task'),
    url(r'^tasks/remove/(?P<pk>\d+)/$', views.delete_task, name='remove_task'),
    url(r'^plans/remove/(?P<pk>\d+)/$', views.remove_plan, name='remove_plan'),
    url(r'^plans/new/$', views.create_plan, name='new_plan'),
    url(r'^plans/add-plan$', views.add_plan, name='add_plan'),
    url(r'^tasks/(?P<pk>\d+)/edit/$', views.edit_task, name='edit_task'),
    url(r'^plans/(?P<pk>\d+)/edit/$', views.edit_plan, name='edit_plan'),
    url(r'^tasks/save-task/$', views.save_task, name='save_task'),
    url(r'^tasks/save-plan/$', views.save_plan, name='save_plan'),
    url(r'^logout/$', views.logout, name='logout')
]
