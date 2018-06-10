from calelib.crud import Calendoola
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .forms import AddTaskForm, AddPlanForm, EditTaskForm, EditPlanForm

db = Calendoola()


def index(request):
    return redirect('tasks')


def tasks(request):
    current = db.current_user.nickname
    tasks_list = db.get_tasks()
    context = {'tasks': tasks_list, 'current': current}
    return render(request, 'caleweb/tasks-views/tasks.html', context)


def plans(request):
    current = db.current_user.nickname
    plans_list = db.get_plans()
    context = {'plans': plans_list, 'current': current}
    return render(request, 'caleweb/plans-views/plans.html', context)


def task(request, pk):
    try:
        single_task = db.get_tasks(pk)
        current = db.current_user.nickname
        context = {'task': single_task, 'current': current}
        return render(request, 'caleweb/tasks-views/task.html', context)
    except ObjectDoesNotExist:
        raise Http404("Task does not exist")


def plan(request, pk):
    try:
        single_plan = db.get_plans(pk)
        current = db.current_user.nickname
        context = {'plan': single_plan, 'current': current}
        return render(request, 'caleweb/plans-views/plan.html', context)
    except ObjectDoesNotExist:
        raise Http404("Plan does not exist")


def create_task(request):
    form = AddTaskForm()
    current = db.current_user.nickname
    context = {'add_form': form, 'current': current}
    return render(request, 'caleweb/tasks-views/create-task.html', context)


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
    current = db.current_user.nickname
    context = {'add_form': form, 'current': current}
    return render(request, 'caleweb/plans-views/create-plan.html', context)


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
    current = db.current_user.nickname
    context = {'form_change': form, 'current': current}
    return render(request, 'caleweb/tasks-views/edit_task.html', context)


@require_POST
def save_task(request):
    db.change_task(request.POST.get('id'), request.POST.get('info', None), request.POST.get('deadline', None),
                   request.POST.get('priority', None), request.POST.get('status', None), None, None)
    return redirect('/')


def edit_plan(request, pk):
    plan = db.get_plans(pk)
    form = EditPlanForm(id=pk, info_old=plan.info, period_type_old=plan.period_type, period_value_old=plan.period,
                        time_at_old=plan.time_at)
    current = db.current_user.nickname
    context = {'form_change': form, 'current': current}
    return render(request, 'caleweb/plans-views/edit_plan.html', context)


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
    if db.current_user.nickname =='SASHA':
        db.current_user = 'guess'
    else:
        db.current_user = 'SASHA'
    return redirect('/')