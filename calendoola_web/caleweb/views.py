from calelib.crud import Calendoola
from calelib.models import Task
from django.contrib.auth import (login,
                                 )
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView
                                  )

from . import value_parsers as vp
from .forms import (
    AddPlanForm,
    EditTaskForm,
    EditPlanForm,
)

db = Calendoola()


# ###T###A###S###K###S###

class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'caleweb/task_all.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_tasks(username)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'caleweb/task_details.html'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_tasks(username)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'caleweb/task_create.html'
    fields = ['info', 'deadline', 'priority', 'tags']

    def form_valid(self, form):
        username = self.request.user.username
        new_task = form.save()
        db.add_completed(username, 'task', new_task)
        return redirect('tasks')


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'caleweb/task_update.html'
    fields = ['info', 'deadline', 'priority', 'tags']
    success_url = '/'


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'caleweb/task_confirm_delete.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(TaskDeleteView, self).get_context_data(**kwargs)
        user = self.request.user.username
        context['tasks'] = db.get_tasks(user)
        return context

    def get_queryset(self):
        username = self.request.user.username
        return db.get_tasks(username)

# ###T###A###S###K###S###


class PlanListView(LoginRequiredMixin, ListView):
    template_name = 'caleweb/plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        username = self.request.user.username

        return db.get_plans(username)


class PlanDetailView(LoginRequiredMixin, DetailView):
    template_name = 'caleweb/plan.html'
    context_object_name = 'plan'

    def get_queryset(self):
        username = self.request.user.username

        return db.get_plans(username)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def index(request):
    return redirect('tasks')


def create_plan(request):
    form = AddPlanForm()

    context = {'add_form': form}
    return render(request, 'caleweb/create-plan.html', context)


@require_POST
def add_plan(request):
    form = AddPlanForm(request.POST)
    if form.is_valid():
        period_type, period_value = vp.parse_period(request.POST.get('period_type'), request.POST.get('period_value'))
        db.create_plan(request.POST.get('info', None), period_value, period_type,
                       request.POST.get('time_at'))
        return redirect('/plans')


def edit_task(request, pk):
    task = db.get_tasks(pk)
    form_data = {'id': pk,
                 'info': task.info,
                 'deadline': task.deadline,
                 'tags': task.tags}
    form = EditTaskForm(form_data)

    context = {'form_change': form}
    return render(request, 'caleweb/edit_task.html', context)


@require_POST
def save_task(request):
    db.change_task(request.POST.get('id'), request.POST.get('info', None), None,
                   request.POST.get('priority', None), request.POST.get('status', None), None, None)
    return redirect('/')


def edit_plan(request, pk):
    plan = db.get_plans(pk)
    form_data = {'id': pk,
                 'info': plan.info,
                 'period_type': plan.period_type,
                 'period_value': plan.period,
                 'time_at': plan.time_at}
    form = EditPlanForm(form_data)

    context = {'form_change': form}
    return render(request, 'caleweb/edit_plan.html', context)


@require_POST
def save_plan(request):
    db.change_plan(request.POST.get('id'), request.POST.get('info'), request.POST.get('period_type'),
                   request.POST.get('period_value'), request.POST.get('time_at'))
    return redirect('/plans')


def remove_plan(request, pk):
    db.remove_plan(pk)
    return redirect('/plans')


def finish_task(request, pk):
    username = request.user.username
    db.get_tasks(username, pk).finish()
    return redirect('/tasks/{}/'.format(pk))


def unfinish_task(request, pk):
    username = request.user.username
    db.get_tasks(username, pk).unfinish()
    return redirect('/tasks/{}/'.format(pk))
