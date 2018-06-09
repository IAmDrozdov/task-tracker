from django.shortcuts import render, redirect
from calelib.crud import Calendoola
from django.template.defaultfilters import register

from .forms import AddTaskForm, AddPlanForm, EditTaskForm
from django.views.decorators.http import require_POST

db = Calendoola()


def index(request):
    return redirect('tasks')


def tasks(request):
    tasks = db.get_tasks()
    return render(request, 'caleweb/home-page.html', {'tasks': tasks})


def task(request, pk):
    task = db.get_tasks(pk)
    return render(request, 'caleweb/task.html', {'task': task})


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
    return redirect('tasks')


def create_plan(request):
    form = AddPlanForm()
    return render(request, 'caleweb/create-plan.html', {'add_form': form})


@require_POST
def add_plan(request):
    form = AddPlanForm(request.POST)
    if form.is_valid():
        db.create_plan(request.POST.get('info', None), request.POST.get('period_value'),
                       request.POST.get('period_type'), request.POST.get('time_at'))
    return redirect('tasks')


def edit_task(request, pk):
    task = db.get_tasks(pk)
    form = EditTaskForm(info_old=task.info, deadline_old=task.deadline, tags_old=task.tags, id=pk)
    return render(request, 'caleweb/edit_task.html', {'form_change': form})


@require_POST
def save_task(request):
    print(request.POST)
    db.change_task(request.POST.get('id'), request.POST.get('info', None),request.POST.get('deadline', None),
                   request.POST.get('priority', None), request.POST.get('status', None), None, None)
    return redirect('tasks')
