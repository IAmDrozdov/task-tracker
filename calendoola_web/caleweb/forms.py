from calelib import Constants
from django import forms
from django.utils import timezone


class AddTaskForm(forms.Form):
    info = forms.CharField(max_length=40, help_text='Enter what to do')
    priority = forms.IntegerField(help_text='1-min .. 5-max', required=True, initial=1)
    deadline = forms.DateTimeField(required=False)
    tags = forms.CharField(max_length=120, required=False, help_text='Use spaces to separate')
    parent_task = forms.CharField(widget=forms.Select(), required=False, help_text='Task to what to append')

    def clean(self):
        cleaned_data = super(AddTaskForm, self).clean()
        info = cleaned_data.get('info')
        priority = cleaned_data.get('priority')
        deadline = cleaned_data.get('deadline')
        if not info:
            raise forms.ValidationError('Write something!')
        elif 0 > int(priority) < 6:
            raise forms.ValidationError('Priority can take values from 1 to 5')
        elif deadline:
            if deadline < timezone.now():
                raise forms.ValidationError('Deadline can not be set earlier than now')


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
