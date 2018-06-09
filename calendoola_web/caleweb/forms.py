from django import forms
from calelib import Constants


class AddTaskForm(forms.Form):
    info = forms.CharField(max_length=40,
                           widget=forms.TextInput(
                               attrs={'class': 'text-input',
                                      'placeholder': 'Enter what to do'}
                           ))
    priority = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'text-input', 'style': 'margin-top:18px',
                                                                  'placeholder': '1-5'}), required=False)
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'text-input', 'style': 'margin-top:36px'
        , 'placeholder': '%Y-%m-%d %H:%M'}), required=False)
    tags = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class': 'text-input',
                                                                        'style': 'margin-top:54px'}), required=False)
    parent_id = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'text-input', 'style': 'margin-top:90px'}),
                                   required=False)


class AddPlanForm(forms.Form):
    info = forms.CharField(max_length=40,
                           widget=forms.TextInput(
                               attrs={'class': 'text-input',
                                      'placeholder': 'Enter what to do'}
                           ))
    period_type = forms.CharField(max_length=20,
                                  widget=forms.Select(choices=(('daily', Constants.REPEAT_DAY),
                                                               ('weekdayly', Constants.REPEAT_WEEKDAY),
                                                               ('monthly', Constants.REPEAT_MONTH),
                                                               ('yearly', Constants.REPEAT_YEAR)),
                                                      attrs={'class': 'text-input',
                                                             'style': 'height=50px; margin-top: 25px;'}))
    period_value = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'text-input',
                                                                                'style': 'margin-top:40px;'}))

    time_at = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'text-input', 'style': 'margin-top:60px',
                                                            'placeholder': '1-5'}))


class EditTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        print(kwargs)
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
