from django.shortcuts import render, redirect
from calelib.crud import Calendoola

from .forms import AddTaskForm, AddPlanForm, EditTaskForm, EditPlanForm
from django.views.decorators.http import require_POST

db = Calendoola()


def index(request):
    return redirect('tasks')


def tasks(request):
    tasks = db.get_tasks()
    return render(request, 'caleweb/tasks.html', {'tasks': tasks})


def plans(request):
    plans = db.get_plans()
    return render(request, 'caleweb/plans.html', {'plans': plans})


def task(request, pk):
    task = db.get_tasks(pk)
    return render(request, 'caleweb/task.html', {'task': task})


def plan(request, pk):
    plan = db.get_plans(pk)
    return render(request, 'caleweb/plan.html', {'plan': plan})


def create_task(request):
    form = AddTaskForm()
    return render(request, 'caleweb/create-task.html', {'add_form': form})


@require_POST
def add_task(request):
    form = AddTaskForm(request.POST)
    if form.is_valid():
        db.create_task(request.POST['info'], request.POST.get('priority', 1), request.POST.get('deadline', None),
                       request.POST.get('tags', '').strip().split(), None)
    return redirect('tasks')


def delete_task(request, pk):
    db.remove_task(pk)
    return redirect('/')


def create_plan(request):
    form = AddPlanForm()
    return render(request, 'caleweb/create-plan.html', {'add_form': form})


@require_POST
def add_plan(request):
    form = AddPlanForm(request.POST)
    if form.is_valid():
        db.create_plan(request.POST.get('info', None), request.POST.get('period_value'),
                       request.POST.get('period_type'), request.POST.get('time_at'))
    return redirect('/plans')


def edit_task(request, pk):
    task = db.get_tasks(pk)
    form = EditTaskForm(info_old=task.info, deadline_old=task.deadline, tags_old=task.tags, id=pk)
    return render(request, 'caleweb/edit_task.html', {'form_change': form})


@require_POST
def save_task(request):
    db.change_task(request.POST.get('id'), request.POST.get('info', None), request.POST.get('deadline', None),
                   request.POST.get('priority', None), request.POST.get('status', None), None, None)
    return redirect('/')


def edit_plan(request, pk):
    plan = db.get_plans(pk)
    form = EditPlanForm(id=pk, info_old=plan.info, period_type_old=plan.period_type, period_value_old=plan.period,
                        time_at_old=plan.time_at)
    return render(request, 'caleweb/edit_plan.html', {'form_change': form})


@require_POST
def save_plan(request):
    db.change_plan(request.POST.get('id'), request.POST.get('info'), request.POST.get('period_type'),
                   request.POST.get('period_value'), request.POST.get('time_at'))
    return redirect('/plans')


def remove_plan(request, pk):
    db.remove_plan(pk)
    return redirect('/plans')
