from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm
from ticket.models import Task
from authentication.models import AuthUser
from authentication.models import Company


class AddEditTaskForm(ModelForm):
    """The picklist showing the users to which a new task can be assigned
    must find other members of the group this TaskList is attached to."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_staff:
            staffs = AuthUser._default_manager.filter(is_staff=True)
            self.fields['assigned_to'].queryset = staffs
            self.fields['assigned_to'].label_from_instance = lambda obj: '%s (%s)' % (
                obj.get_full_name(),
                obj.username,
            )
            self.fields['assigned_to'].widget.attrs = {
                'id': 'id_assigned_to',
                'class': 'custom-select mb-3',
                'name': 'assigned_to',
            }
            self.fields['assigned_to'].required = False

    title = forms.CharField(widget=forms.widgets.TextInput())
    # due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    note = forms.CharField(widget=forms.widgets.TextInput(), required=False)

    class Meta:
        model = Task
        exclude = ['created_by', 'modified_by', 'created_at', 'modified_at']


class AddExternalTaskForm(ModelForm):
    """Form to allow users who are not part of the GTD system to file a ticket."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user.is_staff:
            companies = Company.objects.all()
            self.fields['task_list'].queryset = companies
            self.fields['task_list'].label_from_instance = lambda obj: '%s (%s %s)' % (
                obj.name,
                obj.credits,
                obj.subscription_based
            )
            self.fields['task_list'].widget.attrs = {
                'id': 'id_task_list',
                'class': 'custom-select mb-3',
                'name': 'task_list',
            }
            self.fields['task_list'].required = True

    title = forms.CharField(widget=forms.widgets.TextInput(attrs={'size': 35}), label='Summary')
    note = forms.CharField(widget=forms.widgets.Textarea(), label='Problem Description')
    priority = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Task
        exclude = (
            'created_date',
            'due_date',
            'created_by',
            'modified_by',
            'created_at',
            'modified_at',
            'assigned_to',
            'completed',
            'completed_date',
        )


class SearchForm(forms.Form):
    """Search."""

    q = forms.CharField(widget=forms.widgets.TextInput(attrs={'size': 35}))
