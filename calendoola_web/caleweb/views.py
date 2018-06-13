from calelib.crud import Calendoola
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView
from . import value_parsers as vp
from .forms import AddTaskForm, AddPlanForm, EditTaskForm, EditPlanForm
from calelib.models import Task, User, Plan, Reminder

db = Calendoola()


class TaskListView(ListView):
    template_name = 'caleweb/tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return db.get_tasks()


class TaskDetailView(DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'caleweb/task_details.html'

    def get_queryset(self):
        return db.get_tasks()


class PlanListView(ListView):
    template_name = 'caleweb/plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return db.get_plans()


class PlanDetailView(DetailView):
    template_name = 'caleweb/plan.html'
    context_object_name = 'plan'

    def get_queryset(self):
        return db.get_plans()


class TaskCreateView(CreateView):
    model = Task
    template_name = 'caleweb/task_form.html'
    fields = ['info', 'deadline', 'priority', 'tags']

    def get_queryset(self):
        return db.get_tasks()

    def form_valid(self, form):
        return redirect('tasks')


def index(request):
    return redirect('tasks')


def new_task(request):
    if request.method == 'POST':
        form = AddTaskForm(request.POST)
        if form.is_valid():
            deadline = None if not form['deadline'].value() else form['deadline'].value()
            priority = 1 if not form['priority'].value() else int(form['priority'].value())
            if not form['parent_task'].value():
                db.create_task(form['info'].value(), priority, deadline, form['tags'].value().strip().split())
            else:
                db.create_task(form['info'].value(), priority, deadline,
                               form['tags'].value().strip().split(), int(form['parent_task'].value()))
            return redirect('/')
    else:
        form = AddTaskForm()
        tuple_tasks = [(str(t.pk), t.info[:10]) for t in db.get_tasks()]
        form.fields['parent_task'].widget.choices = [('', 'no'), ] + tuple_tasks
        context = {'add_form': form}
        return render(request, 'caleweb/create-task.html', context)


def delete_task(request, pk):
    db.remove_task(pk)
    return redirect('/')


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
    db.get_tasks(pk).finish()
    return redirect('/tasks/{}/'.format(pk))


def unfinish_task(request, pk):
    db.get_tasks(pk).unfinish()
    return redirect('/tasks/{}/'.format(pk))


def logout(request):
    if db.current_user.nickname == 'SASHA':
        db.current_user = 'guess'
    else:
        db.current_user = 'SASHA'
    return redirect('/')
