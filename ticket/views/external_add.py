from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from ticket.defaults import defaults
from ticket.forms import AddExternalTaskForm


@login_required
def external_add(request) -> HttpResponse:
    """Allow authenticated users who don't have access to the rest of the ticket system to file a ticket
    in the list specified in settings (e.g. cs-support-ticket can be used a ticket filing system for a school, where
    students can file tickets without access to the rest of the ticket system).

    Publicly filed tickets are unassigned unless settings.DEFAULT_ASSIGNEE exists.
    """

    if request.POST:
        form = AddExternalTaskForm(request.user, request.POST)
        if form.is_valid():
            current_site = Site.objects.get_current()
            task = form.save(commit=False)
            if not request.user.is_staff:
                task.task_list = request.user.company
            if request.user.is_staff:
                task.assigned_to = request.user
            if defaults('TICKET_DEFAULT_ASSIGNEE'):
                task.assigned_to = get_user_model().objects.get(username=settings.TICKET_DEFAULT_ASSIGNEE)
            task.save()

            # Send email to assignee if we have one
            if task.assigned_to:
                email_subject = render_to_string(
                    'ticket/email/assigned_subject.txt', {'task': task.title}
                )
                email_body = render_to_string(
                    'ticket/email/assigned_body.txt', {'task': task, 'site': current_site}
                )
                try:
                    send_mail(
                        email_subject,
                        email_body,
                        task.created_by.email,
                        [task.assigned_to.email],
                        fail_silently=False,
                    )
                except ConnectionRefusedError:
                    messages.warning(
                        request, "Task saved but mail not sent. Contact your administrator."
                    )

            messages.success(
                request, "Your trouble ticket has been submitted. We'll get back to you soon."
            )
            return redirect(defaults("TICKET_PUBLIC_SUBMIT_REDIRECT"))
    else:
        form = AddExternalTaskForm(request.user)

    context = {'form': form}

    return render(request, 'ticket/add_task_external.html', context)
