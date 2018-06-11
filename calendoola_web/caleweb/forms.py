from calelib import Constants
from django import forms


class AddTaskForm(forms.Form):
    info = forms.CharField(max_length=40, help_text='Enter what to do')
    priority = forms.IntegerField(help_text='1-min .. 5-max', required=False)
    deadline = forms.DateTimeField(required=False)
    tags = forms.CharField(max_length=120, required=False, help_text='Use spaces to separate')
    parent_task_id = forms.CharField(widget=forms.Select())


class AddPlanForm(forms.Form):
    info = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter what to do'}
        ))
    period_type = forms.CharField(
        widget=forms.Select(choices=((Constants.REPEAT_DAY, 'daily'),
                                     (Constants.REPEAT_WEEKDAY, 'weekdaly'),
                                     (Constants.REPEAT_MONTH, 'monthly'),
                                     (Constants.REPEAT_YEAR, 'yearly'))))
    period_value = forms.CharField(widget=forms.TextInput())

    time_at = forms.TimeField(required=False)


class EditTaskForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    info = forms.CharField(max_length=40, widget=forms.TextInput(), required=False)
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(), required=False)
    tags = forms.CharField(widget=forms.TextInput(), required=False)


class EditPlanForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    info = forms.CharField(max_length=40, widget=forms.TextInput(), required=False)
    period_type = forms.CharField(widget=forms.TextInput(), required=False)
    period_value = forms.CharField(widget=forms.TextInput(), required=False)
    time_at = forms.CharField(widget=forms.TextInput(), required=False)
