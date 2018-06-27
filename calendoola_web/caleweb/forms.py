from calelib.constants import Constants
from calelib.models import (
    Task,
    Plan,
)
from django import forms

from .value_parsers import parse_period


class TaskShareForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._users = kwargs.pop('users')
        super(TaskShareForm, self).__init__(*args, **kwargs)
        self.fields['user_to'].choices = ((u.nickname, u.nickname) for u in self._users)

    user_to = forms.ChoiceField(widget=forms.Select, label='Users')


class TaskCreateForm(forms.ModelForm):
    parent_task = forms.ModelChoiceField(empty_label='Do not make subtask',
                                         queryset=Task.objects.none(),
                                         required=False)

    def __init__(self, tasks, *args, **kwargs):
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        self.fields['parent_task'].queryset = tasks

    class Meta:
        model = Task
        fields = ['info', 'deadline', 'priority', 'tags']


class AddSubtaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self._parent_task = kwargs.pop('parent_task')
        super(AddSubtaskForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Task
        fields = ['info', 'deadline', 'priority', 'tags']

    def clean_deadline(self):
        if self._parent_task.deadline and self.cleaned_data['deadline']:
            if self._parent_task.deadline < self.cleaned_data['deadline']:
                self.add_error('deadline', 'Deadline of child task can not exceed {}'
                               .format(self._parent_task.deadline.strftime('%d %m %Y %H:%M ')))


class TaskMoveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._tasks = kwargs.pop('tasks')
        super(TaskMoveForm, self).__init__(*args, **kwargs)
        self.fields['task_to'].choices = ((t.pk, t.info) for t in self._tasks)
        if len(self.fields['task_to'].choices) == 0:
            self.fields['task_to'].widget = forms.HiddenInput()

    to_main = forms.BooleanField(required=False, help_text='Pass task to main view',
                                 widget=forms.Select(choices=((False, 'No'),
                                                              (True, 'Yes')
                                                              )))
    task_to = forms.ChoiceField(label='Available tasks')


class PlanModelForm(forms.ModelForm):
    period = forms.CharField(widget=forms.TextInput(), initial='')

    class Meta:
        model = Plan
        fields = ['info', 'time_at', 'period_type']

    def clean(self):
        cleaned_data = super(PlanModelForm, self).clean()
        try:
            parse_period(cleaned_data['period_type'], cleaned_data['period'])
        except ValueError:
            if cleaned_data['period_type'] == Constants.REPEAT_DAY:
                self.add_error('period', 'Enter only digit')
            elif cleaned_data['period_type'] == Constants.REPEAT_WEEKDAY:
                self.add_error('period', 'Enter only full weekday names')
            else:
                self.add_error('period', 'Follow example: "25 May, October"')


class ReminderAddTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._tasks = kwargs.pop('task')
        super(ReminderAddTaskForm, self).__init__(*args, **kwargs)
        self.fields['task'].choices = ((t.pk, t.info) for t in self._tasks)

    task = forms.ChoiceField(label='Available tasks', required=False)
