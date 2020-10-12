from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from authentication.models import Company
from ticket.forms import AddEditTaskForm
from ticket.models import Task
from ticket.utils import send_notify_mail

import bleach


@login_required
def my_list_detail(request, view_completed=False) -> HttpResponse:
    """Display and manage tasks in a ticket list.
    """

    # Defaults
    task_list = None
    form = None
    list_slug = None
    ticket_slug = 'mine'

    # Which tasks to show on this list view?
    if request.user.is_staff:
        if request.user.is_superuser:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(assigned_to=request.user)
        list_slug = request.user.get_full_name()
    else:
        task_list = request.user.company
        tasks = Task.objects.filter(task_list=task_list)
        list_slug = task_list.name

    # Additional filtering
    if view_completed:
        tasks = tasks.filter(completed=True)
    else:
        tasks = tasks.filter(completed=False)


    # ######################
    #  Add New Task Form
    # ######################
    if not request.POST.getlist('add_edit_task'):
        form = AddEditTaskForm(request.user, initial={'priority': 999, 'task_list': task_list})
    else:
        form = AddEditTaskForm(request.user, request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.note = bleach.clean(form.cleaned_data['note'], strip=True)
            new_task.title = bleach.clean(form.cleaned_data['title'], strip=True)
            new_task.save()
            return redirect(request.path)
        else:
            messages.error(request, "Task creation something went wrong!!!")

    context = {
        'list_slug': list_slug,
        'ticket_slug': ticket_slug,
        'form': form,
        'tasks': tasks,
        'view_completed': view_completed,
    }

    return render(request, 'ticket/list_detail.html', context)
