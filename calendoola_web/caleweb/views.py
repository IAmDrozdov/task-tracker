from calelib.crud import Calendoola
from calelib.models import Task
from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView, )
from django.contrib.auth.decorators import login_required

from . import value_parsers as vp
from .forms import (
    AddPlanForm,
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
        new_task = form.save(commit=False)
        new_task.owner = self.request.user.username
        new_task.save()
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

    def get_queryset(self):
        username = self.request.user.username
        return db.get_tasks(username)


class TaskShareForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        super(TaskShareForm, self).__init__()
        self.fields['user_to'].choices = ((u.nickname, u.nickname) for u in db.get_users().exclude(nickname=self.user))
    user_to = forms.ChoiceField(widget=forms.Select, label='Users')


@login_required
def share_task(request, pk):
    if request.method == 'POST':
        form = TaskShareForm(request.POST)
        username = db.get_users(username=request.user.username)
        user_to = db.get_users(username=request.POST['user_to'])
        task_to_share = db.get_tasks(username, pk)
        user_to.add_task(task_to_share)
        task_to_share.add_performer(user_to.nickname)
        return redirect('/')

    form = TaskShareForm(user=request.user.username)
    return render(request, 'caleweb/task_share.html', {'form': form})


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
