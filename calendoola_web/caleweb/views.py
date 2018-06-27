from calelib import CycleError
from calelib.crud import Calendoola
from calelib.models import (
    Task,
    Plan,
    Reminder,
)
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import (
    TaskShareForm,
    TaskCreateForm,
    PlanModelForm,
    ReminderAddTaskForm,
    AddSubtaskForm,
    TaskMoveForm,
)
from .value_parsers import (
    parse_period,
    parse_period_to_view,
)

db = Calendoola()


def signup(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# ###R###E###G###I###S###T###R###A###T###I###O###N##########

@login_required
def finish_task(request, pk):
    username = request.user.username
    task = db.get_tasks(username, pk)
    task.finish()
    return redirect('homepage')


@login_required
def restore_task(request, pk):
    username = request.user.username
    task = db.get_tasks(username, pk)
    task.restore()
    return redirect('homepage')


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
            result_info = db.get_tasks(username, info=query, primary=False)
            result_tags = db.get_tasks(username, tags=query, primary=False)
            result = result_info | result_tags
        return result


class TaskArchiveListView(LoginRequiredMixin, ListView):
    template_name = 'caleweb/task_all.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_tasks(username=username, archive=True)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'caleweb/task_detail.html'

    def get_object(self, queryset=None):
        return db.get_tasks(username=self.request.user.username, task_id=self.kwargs['pk'])


class TaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = 'caleweb/instance-form.html'

    def get_form_kwargs(self):
        kwargs = super(TaskCreateView, self).get_form_kwargs()
        kwargs.update({'tasks': db.get_tasks(self.request.user.username, primary=False)})
        return kwargs

    def form_valid(self, form):
        username = self.request.user.username
        new_task = form.save(commit=False)
        new_task.owner = db.get_users(self.request.user.username)
        new_task.save()
        parent_task = form.cleaned_data['parent_task']
        parent_task.add_subtask(new_task) if parent_task else db.add_completed(username, 'task', new_task)
        return redirect('tasks:detail', new_task.pk)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'caleweb/instance-form.html'
    fields = ['info', 'deadline', 'priority', 'tags']

    def get_success_url(self):
        return reverse_lazy('tasks:detail', args=(self.object.pk,))


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'caleweb/confirm_delete-form.html'
    success_url = reverse_lazy('homepage')

    def get_object(self, queryset=None):
        username = self.request.user.username
        task = db.get_tasks(username=username,
                            task_id=self.kwargs['pk'])
        return task

    def delete(self, request, *args, **kwargs):
        username = self.request.user.username
        db.remove_task(username, self.kwargs['pk'])
        return redirect('homepage')


class AddSubtaskView(CreateView):
    form_class = AddSubtaskForm
    template_name = 'caleweb/instance-form.html'

    def get_form_kwargs(self):
        kwargs = super(AddSubtaskView, self).get_form_kwargs()
        parent_task = db.get_tasks(self.request.user.username, self.kwargs['pk'])
        kwargs.update({'parent_task': parent_task})
        return kwargs

    def form_valid(self, form):
        username = self.request.user.username
        parent_task = db.get_tasks(username, self.kwargs['pk'])
        new_task = form.save(commit=False)
        new_task.owner = db.get_users(self.request.user.username)
        new_task.save()
        parent_task.add_subtask(new_task)
        return redirect('tasks:detail', self.kwargs['pk'])


def check_possible_tasks(username, id_from, id_to):
    try:
        task_from = db.get_tasks(username, id_from)
        task_from.is_parent(id_to)
    except CycleError:
        return False
    else:
        return True


@login_required
def move_task(request, pk):
    username = request.user.username
    task = db.get_tasks(username, pk)
    pks_to_exclude = [pk] if not task.parent_task else [pk, task.parent_task.pk]
    tasks = db.get_tasks(username).exclude(pk__in=pks_to_exclude)
    available_tasks = (t for t in tasks if check_possible_tasks(username, pk, t.pk))
    form = TaskMoveForm(request.POST or None, tasks=available_tasks)
    if request.method == 'POST':
        task_from = db.get_tasks(username=username, task_id=pk)

        if form.is_valid():
            if form.cleaned_data['to_main']:
                task_from.parent_task = None
                task_from.save()
                db.add_completed(username, 'task', task_from)

            elif request.POST.get('task_to', None):
                task_to = db.get_tasks(username=username, task_id=form.cleaned_data['task_to'])
                task_to.add_subtask(task_from)

            return redirect('homepage')
    return render(request, 'caleweb/task_move.html', {'form': form})


@login_required
def share_task(request, pk):
    users = db.get_users().exclude(nickname=request.user.username)
    form = TaskShareForm(request.POST or None, users=users)

    if request.method == 'POST':
        if form.is_valid():
            username = db.get_users(username=request.user.username)
            user_to = db.get_users(username=form.cleaned_data['user_to'])
            task_to_share = db.get_tasks(username, pk)
            user_to.apply_task(task_to_share)
            return redirect('homepage')
    return render(request, 'caleweb/task_share.html', {'form': form})


@login_required
def unshare_task(request, pk, name):
    username = request.user.username
    task = db.get_tasks(username, pk)
    performer = db.get_users(name)
    performer.detach_task(task)
    return redirect('tasks:detail', pk)


# ###T###A###S###K###S###################################


class PlanListView(LoginRequiredMixin, ListView):
    template_name = 'caleweb/plan_all.html'
    context_object_name = 'plans'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_plans(username)


class PlanCreateView(LoginRequiredMixin, CreateView):
    model = Plan
    form_class = PlanModelForm
    template_name = 'caleweb/instance-form.html'

    def form_valid(self, form):
        username = self.request.user.username
        new_plan = form.save(commit=False)
        new_plan.period = parse_period(new_plan.period_type, self.request.POST['period'])
        new_plan.save()
        db.add_completed(username, 'plan', new_plan)
        return redirect('plans:all')


class PlanDeleteView(LoginRequiredMixin, DeleteView):
    model = Plan
    template_name = 'caleweb/confirm_delete-form.html'
    success_url = reverse_lazy('plans:all')

    def get_queryset(self):
        return db.get_plans(self.request.user.username)


@login_required
def plan_set_state(request, pk):
    username = db.get_users(request.user.username)
    plan = db.get_plans(username, pk)
    plan.set_state()
    return redirect('plans:all')


class PlanUpdateView(LoginRequiredMixin, UpdateView):
    model = Plan
    template_name = 'caleweb/instance-form.html'
    form_class = PlanModelForm
    success_url = reverse_lazy('plans:all')

    def get_initial(self):
        plan = db.get_plans(self.request.user.username, self.kwargs['pk'])
        return {'period': parse_period_to_view(plan.period_type, plan.period)}

    def form_valid(self, form):
        username = self.request.user.username
        new_plan = form.save(commit=False)
        new_plan.period = parse_period(new_plan.period_type, self.request.POST['period'])
        new_plan.save()
        db.add_completed(username, 'plan', new_plan)
        return redirect('plans:all')


# ###P###L###A###N###S##############################################


class ReminderListView(LoginRequiredMixin, ListView):
    model = Reminder
    template_name = 'caleweb/reminder-all.html'
    context_object_name = 'reminders'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_reminders(username)


class ReminderCreateView(LoginRequiredMixin, CreateView):
    model = Reminder
    template_name = 'caleweb/instance-form.html'
    fields = ['remind_type', 'remind_before']

    def form_valid(self, form):
        username = self.request.user.username
        new_reminder = form.save()
        db.add_completed(username, 'reminder', new_reminder)
        return redirect('reminders:detail', new_reminder.pk)


class ReminderDeleteView(LoginRequiredMixin, DeleteView):
    model = Reminder
    template_name = 'caleweb/confirm_delete-form.html'
    success_url = reverse_lazy('reminders:all')


class ReminderDetailView(LoginRequiredMixin, DetailView):
    model = Reminder
    context_object_name = 'reminder'
    template_name = 'caleweb/reminder-detail.html'

    def get_queryset(self):
        username = self.request.user.username
        return db.get_reminders(username)


@login_required
def reminder_set_state(request, pk):
    username = db.get_users(request.user.username)
    reminder = db.get_reminders(username, pk)
    reminder.set_state()
    return redirect('reminders:all')


class ReminderUpdateView(LoginRequiredMixin, UpdateView):
    model = Reminder
    template_name = 'caleweb/instance-form.html'
    fields = ['remind_type', 'remind_before']

    def get_success_url(self):
        return reverse_lazy('reminders:detail', args=(self.object.pk,))


@login_required
def reminder_add_task(request, pk):
    username = db.get_users(request.user.username)
    reminder = db.get_reminders(username, pk)
    tasks_ids = [t.pk for t in reminder.get_tasks()]
    tasks = db.get_tasks(username, primary=False).exclude(pk__in=tasks_ids).exclude(deadline__isnull=True)

    form = ReminderAddTaskForm(request.POST or None, task=tasks)
    if request.method == 'POST':
        if form.is_valid():
            task = db.get_tasks(username=username, task_id=form.cleaned_data['task'])
            reminder.apply_task(task)
            return redirect('reminders:detail', pk)

    return render(request, 'caleweb/reminder_add_task.html', {'form': form})


@login_required
def reminder_detach_task(request, pk, task):
    username = request.user.username
    reminder = db.get_reminders(username, pk)
    task = db.get_tasks(username, task)
    reminder.detach_task(task)
    return redirect('reminders:detail', pk)
