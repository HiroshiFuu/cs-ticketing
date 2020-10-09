from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ticket.defaults import defaults
from ticket.features import HAS_TASK_MERGE
from ticket.forms import AddEditTaskForm
from ticket.models import Attachment, Comment, Task
from ticket.utils import (
    send_email_to_thread_participants,
    staff_check,
    toggle_task_completed,
    user_can_read_task,
)

if HAS_TASK_MERGE:
    from dal import autocomplete

import datetime
import os
import bleach


def handle_add_comment(request, task):
    if not request.POST.get("add_comment"):
        return

    Comment.objects.create(
        author=request.user, task=task, body=bleach.clean(
            request.POST["comment-body"], strip=True)
    )

    send_email_to_thread_participants(
        task,
        request.POST["comment-body"],
        request.user,
        subject='New comment posted on task "{}"'.format(task.title),
    )

    messages.success(
        request, "Comment posted. Notification email sent to thread participants.")


@login_required
def task_detail(request, task_id: int) -> HttpResponse:
    """View task details. Allow task details to be edited. Process new comments on task.
    """

    task = get_object_or_404(Task, pk=task_id)
    comment_list = Comment.objects.filter(task=task_id).order_by("-date")

    # Ensure user has permission to view task. Superusers can view all tasks.
    if not user_can_read_task(task, request.user):
        raise PermissionDenied

    # Handle task merging
    if not HAS_TASK_MERGE:
        merge_form = None
    else:
        class MergeForm(forms.Form):
            merge_target = forms.ModelChoiceField(
                queryset=Task.objects.all(),
                widget=autocomplete.ModelSelect2(
                    url=reverse('ticket:task_autocomplete',
                                kwargs={'task_id': task_id})
                ),
            )

        # Handle task merging
        if not request.POST.get('merge_task_into'):
            merge_form = MergeForm()
        else:
            merge_form = MergeForm(request.POST)
            if merge_form.is_valid():
                merge_target = merge_form.cleaned_data['merge_target']
            if not user_can_read_task(merge_target, request.user):
                raise PermissionDenied

            task.merge_into(merge_target)
            return redirect(reverse('ticket:task_detail', kwargs={'task_id': merge_target.pk}))

    # Save submitted comments
    handle_add_comment(request, task)

    # Save task edits
    if not request.POST.get('add_edit_task'):
        form = AddEditTaskForm(request.user, instance=task)
    else:
        form = AddEditTaskForm(request.user, request.POST, instance=task)

        if form.is_valid():
            edit_task = form.save(commit=False)
            edit_task.note = bleach.clean(form.cleaned_data['note'], strip=True)
            edit_task.title = bleach.clean(form.cleaned_data['title'], strip=True)
            edit_task.save()
            messages.success(request, "The task has been edited.")
            return redirect('ticket:task_detail', task_id=task.id)
            if request.user.is_staff:
                return redirect('ticket:list_detail', company_id=task.task_list.id)
            else:
                return redirect('ticket:my_list_detail')

    # Mark complete
    if request.POST.get('toggle_done'):
        results_changed = toggle_task_completed(task.id)
        if results_changed:
            messages.success(request, f"Changed completion status for task {task.id}")

        return redirect('ticket:task_detail', task_id=task.id)

    if task.due_date:
        thedate = task.due_date
    else:
        thedate = datetime.datetime.now()

    # Handle uploaded files
    if request.FILES.get('attachment_file_input'):
        file = request.FILES.get('attachment_file_input')

        if file.size > defaults('TICKET_MAXIMUM_ATTACHMENT_SIZE'):
            messages.error(request, f'File exceeds maximum attachment size.')
            return redirect('ticket:task_detail', task_id=task.id)

        name, extension = os.path.splitext(file.name)

        if extension not in defaults('TICKET_LIMIT_FILE_ATTACHMENTS'):
            messages.error(request, f'This site does not allow upload of {extension} files.')
            return redirect('ticket:task_detail', task_id=task.id)

        Attachment.objects.create(
            task=task, added_by=request.user, timestamp=datetime.datetime.now(), file=file
        )
        messages.success(request, f'File attached successfully')
        return redirect('ticket:task_detail', task_id=task.id)

    context = {
        'task': task,
        'comment_list': comment_list,
        'form': form,
        'merge_form': merge_form,
        'thedate': thedate,
        'comment_classes': defaults('TICKET_COMMENT_CLASSES'),
        'attachments_enabled': defaults('TICKET_ALLOW_FILE_ATTACHMENTS'),
    }

    return render(request, 'ticket/task_detail.html', context)
