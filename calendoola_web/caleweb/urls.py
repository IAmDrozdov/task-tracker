from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^tasks/$', views.tasks, name='tasks'),
    url(r'^$', views.index, name='homepage'),
    url(r'^tasks/(?P<pk>\d+)/$', views.task, name='task'),
    url(r'^tasks/create-task/$', views.create_task, name='create_task'),
    url(r'^tasks/add-task$', views.add_task, name='add_task'),
    url(r'tasks/remove/(?P<pk>\d+)/$', views.delete_task, name='remove_task'),
    url(r'plans/create-plan$', views.create_plan, name='create_plan'),
    url(r'^plans/add-plan$', views.add_plan, name='add_plan'),
]
