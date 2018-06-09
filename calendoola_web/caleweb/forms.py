from calelib import Constants
from django import forms


class AddTaskForm(forms.Form):
    info = forms.CharField(max_length=40,  widget=forms.TextInput(attrs={'placeholder': 'Enter what to do'}))
    priority = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': '1-5'}), required=False)
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'placeholder': '%Y-%m-%d %H:%M'}), required=False)
    tags = forms.CharField(max_length=40, widget=forms.TextInput(), required=False)
    parent_id = forms.IntegerField(widget=forms.NumberInput(), required=False)


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

    time_at = forms.TimeField(widget=forms.TimeInput(), required=False)


class EditTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.tags_old = kwargs.pop('tags_old')
        self.info_old = kwargs.pop('info_old')
        self.deadline_old = kwargs.pop('deadline_old')
        self.task_id = kwargs.pop('id')
        super(EditTaskForm, self).__init__(*args, **kwargs)
        self.fields['info'].initial = self.info_old
        self.fields['tags'].initial = ' '.join(self.tags_old)
        self.fields['deadline'].initial = self.deadline_old
        self.fields['id'].initial = self.task_id

    id = forms.CharField(widget=forms.HiddenInput())
    info = forms.CharField(max_length=40, widget=forms.TextInput(), required=False)
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(), required=False)
    tags = forms.CharField(widget=forms.TextInput(), required=False)


class EditPlanForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.info = kwargs.pop('info_old')
        self.time_at = kwargs.pop('time_at_old')
        self.period_value = kwargs.pop('period_value_old')
        self.period_type = kwargs.pop('period_type_old')
        self.plan_id = kwargs.pop('id')
        super(EditPlanForm, self).__init__(*args, **kwargs)
        self.fields['info'].initial = self.info
        self.fields['id'].initial = self.plan_id
        self.fields['time_at'].initial = self.time_at
        self.fields['period_type'].initial = self.period_type
        self.fields['period_value'].initial = self.period_value

    id = forms.CharField(widget=forms.HiddenInput())
    info = forms.CharField(max_length=40, widget=forms.TextInput(), required=False)
    period_type = forms.CharField(widget=forms.TextInput(), required=False)
    period_value = forms.CharField(widget=forms.TextInput(), required=False)
    time_at = forms.CharField(widget=forms.TextInput(), required=False)
