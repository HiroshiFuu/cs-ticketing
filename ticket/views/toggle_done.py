from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from ticket.models import Task
from ticket.utils import toggle_task_completed
from ticket.utils import staff_check


@login_required
@user_passes_test(staff_check)
def toggle_done(request, task_id: int) -> HttpResponse:
    """Toggle the completed status of a task from done to undone, or vice versa.
    Redirect to the list from which the task came.
    """

    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_id)

        redir_url = reverse(
            'ticket:list_detail', kwargs={'company_id': task.task_list.id},
        )

        # Permissions
        if not request.user.is_superuser and task.assigned_to != request.user:
            raise PermissionDenied

        credits = request.POST.get('credits_comsumed', None)
        try:
            credits = float(credits)
            toggle_task_completed(task.id, credits)
            messages.success(request, "Task status changed for '{}'".format(task.title))
        except:
            print('Credits Comumed Err')
            messages.error(request, "Error in credits comumed input")

        return redirect(redir_url)
    else:
        raise PermissionDenied
