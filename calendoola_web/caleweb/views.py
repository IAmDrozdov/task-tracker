from calelib.constants import Constants
from calelib.crud import Calendoola
from calelib.models import Task, Plan
from django import forms
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .value_parsers import parse_period, parse_period_to_view
from django.urls import reverse, reverse_lazy
from calelib import CycleError
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView, )

db = Calendoola()


def index(request):
    return redirect('tasks')


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


# ###T###A###S###K###S###

@login_required
def finish_task(request, pk):
    username = request.user.username
    task = db.get_tasks(username, pk)
    task.finish()
    task.pass_to_archive()

    return redirect('/tasks/archive/')


@login_required
def restore_task(request, pk):
    username = request.user.username
    task = db.get_tasks(username, pk)
    task.restore_from_archive()
    task.unfinish()
    return redirect('/')


class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'caleweb/task_all.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        username = self.request.user.username
        if self.request.GET.get('order'):
            return db.get_sorted_tasks(username, self.request.GET.get('order'), self.request.GET.get('vec'))
        return db.get_tasks(username)


class TaskListSearchView(TaskListView):

    def get_queryset(self):
        username = self.request.user.username
        query = self.request.GET.get('data')
        result = db.get_tasks(username)
        if query:
            result_info = db.get_tasks(username, info=query)
            result_tags = db.get_tasks(username, tags=query)
            result = result_info | result_tags
        return result


class TaskArchiveListView(LoginRequiredMixin, ListView):
    template_name = 'caleweb/task_all.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_tasks(username, archive=True)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'caleweb/task_details.html'

    def get_object(self, queryset=None):
        return db.get_tasks(username=self.request.user.username, task_id=self.kwargs['pk'])


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'caleweb/create-form.html'
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
    template_name = 'caleweb/update-form.html'
    fields = ['info', 'deadline', 'priority', 'tags']

    def get_success_url(self):
        return reverse('task-details', args=[self.kwargs['pk']])


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'caleweb/confirm_delete-form.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return db.get_tasks(self.request.user.username, self.kwargs['pk'])


class TaskShareForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        super(TaskShareForm, self).__init__()
        users = db.get_users().exclude(nickname=self.user)
        self.fields['user_to'].choices = ((u.nickname, u.nickname) for u in users)

    user_to = forms.ChoiceField(widget=forms.Select, label='Users')


@login_required
def share_task(request, pk):
    if request.method == 'POST':
        username = db.get_users(username=request.user.username)
        user_to = db.get_users(username=request.POST['user_to'])
        task_to_share = db.get_tasks(username, pk)
        user_to.add_task(task_to_share)
        task_to_share.add_performer(user_to.nickname)
        return redirect('/')
    form = TaskShareForm(user=request.user.username)
    return render(request, 'caleweb/task_share.html', {'form': form})


def check_possible_tasks(username, id_from, id_to):
    try:
        task_from = db.get_tasks(username, id_from)
        task_from.is_parent(id_to)
    except CycleError:
        return False
    else:
        return True


class TaskMoveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user')
        self.task = kwargs.get('task')
        super(TaskMoveForm, self).__init__()
        tasks = db.get_tasks(self.user).exclude(pk=self.task)
        self.fields['task_to'].choices = ((t.pk, t.info) for t in tasks
                                          if check_possible_tasks(self.user, self.task, t.pk))

    to_main = forms.NullBooleanField(help_text='Pass task to main view',
                                     widget=forms.Select(choices=((1, 'No'), (2, 'Yes'))))
    task_to = forms.ChoiceField(label='Available tasks')


@login_required
def move_task(request, pk):
    username = request.user.username

    if request.method == 'POST':
        task_from = db.get_tasks(username=username, task_id=pk)
        if request.POST['to_main'] == '2':
            db.add_completed(username, 'task', task_from.get_copy())
            db.remove_task(username, pk)
        else:
            task_to = db.get_tasks(username=username, task_id=request.POST['task_to'])
            task_to.add_subtask(task_from.get_copy())
            db.remove_task(username, pk)
        return redirect('/')
    form = TaskMoveForm(user=username, task=pk)
    return render(request, 'caleweb/task_move.html', {'form': form})


def unshare_task(request, pk, name):
    username = request.user.username
    task = db.get_tasks(username, pk)
    performer = db.get_users(name)
    performer.tasks.remove(task)
    task.remove_performer(name)
    return redirect('/tasks/{}/'.format(pk))


# ###T###A###S###K###S###


class PlanListView(LoginRequiredMixin, ListView):
    template_name = 'caleweb/plan_all.html'
    context_object_name = 'plans'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_plans(username)


class PlanModelForm(forms.ModelForm):
    period = forms.CharField(widget=forms.TextInput(), initial='')

    class Meta:
        model = Plan
        fields = ['info', 'time_at', 'period_type']

    def clean(self):
        cleaned_data = super(PlanModelForm, self).clean()
        print(cleaned_data)
        try:
            parse_period(cleaned_data['period_type'], cleaned_data['period'])
        except ValueError:
            if cleaned_data['period_type'] == Constants.REPEAT_DAY:
                self.add_error('period', 'Enter only digit')
            elif cleaned_data['period_type'] == Constants.REPEAT_WEEKDAY:
                self.add_error('period', 'Enter only full weekday names')
            else:
                self.add_error('period', 'Follow example: "25 May, October"')


class PlanCreateView(LoginRequiredMixin, CreateView):
    model = Plan
    form_class = PlanModelForm
    template_name = 'caleweb/create-form.html'

    def form_valid(self, form):
        username = self.request.user.username
        new_plan = form.save(commit=False)
        new_plan.period = parse_period(new_plan.period_type, self.request.POST['period'])
        new_plan.save()
        db.add_completed(username, 'plan', new_plan)
        return redirect('plans')


class PlanDeleteView(LoginRequiredMixin, DeleteView):
    model = Plan
    template_name = 'caleweb/confirm_delete-form.html'
    success_url = reverse_lazy('plans')

    def get_queryset(self):
        return db.get_plans(self.request.user.username)


def plan_set_state(request, pk):
    username = db.get_users(request.user.username)
    plan = db.get_plans(username, pk)
    plan.set_state()
    return redirect('plans')


class PlanUpdateView(LoginRequiredMixin, UpdateView):
    model = Plan
    template_name = 'caleweb/update-form.html'
    form_class = PlanModelForm
    success_url = reverse_lazy('plans')

    def get_initial(self):
        plan = db.get_plans(self.request.user.username, self.kwargs['pk'])
        return {'period': parse_period_to_view(plan.period_type, plan.period)}

    def form_valid(self, form):
        username = self.request.user.username
        new_plan = form.save(commit=False)
        new_plan.period = parse_period(new_plan.period_type, self.request.POST['period'])
        new_plan.save()
        db.add_completed(username, 'plan', new_plan)
        return redirect('plans')
