from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from authentication.models import Company
from ticket.forms import AddEditTaskForm
from ticket.models import Task
from ticket.utils import staff_check
from ticket.utils import send_notify_mail

import bleach


@login_required
@user_passes_test(staff_check)
def list_detail(request, company_id=None, view_completed=False) -> HttpResponse:
    """Display and manage tasks in a ticket list.
    """

    # Defaults
    task_list = None
    form = None
    list_slug = None
    ticket_slug = 'slug'

    # Show a specific list, ensuring permissions.
    task_list = get_object_or_404(Company, id=company_id)
    if task_list != request.user.company and not request.user.is_staff:
        raise PermissionDenied
    list_slug = task_list.name
    tasks = Task.objects.filter(task_list=task_list.id)

    # Additional filtering
    if view_completed:
        tasks = tasks.filter(completed=True)
    else:
        tasks = tasks.filter(completed=False)


    # ######################
    #  Add New Task Form
    # ######################

    if request.POST.getlist('add_edit_task'):
        form = AddEditTaskForm(
            request.user,
            request.POST,
            initial={
                'priority': 999,
                'task_list': task_list
            },
        )

        if form.is_valid():
            new_task = form.save()
            # Send email alert only if Notify checkbox is checked AND assignee is not same as the submitter
            if ('notify' in request.POST and new_task.assigned_to and new_task.assigned_to != request.user):
                send_notify_mail(new_task)
            messages.success(
                request, "New task '{t}' has been added.".format(t=new_task.title))
            return redirect(request.path)
    else:
        # Don't allow adding new tasks on some views
        if list_slug not in ['recent-add', 'recent-complete']:
            form = AddEditTaskForm(
                request.user,
                initial={'priority': 999, 'task_list': task_list},
            )

    context = {
        'company_id': company_id,
        'list_slug': list_slug,
        'ticket_slug': ticket_slug,
        'task_list': task_list,
        'form': form,
        'tasks': tasks,
        'view_completed': view_completed,
    }

    return render(request, 'ticket/list_detail.html', context)
