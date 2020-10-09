from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render

from authentication.models import Company
from ticket.forms import SearchForm
from ticket.models import Task
from ticket.utils import staff_check

import datetime


@login_required
@user_passes_test(staff_check)
def list_lists(request) -> HttpResponse:
    '''Homepage view - list of lists a user can view, and ability to add a list.
    '''

    searchform = SearchForm(auto_id=False)

    if request.user.is_staff:
        lists = Company.objects.all()
    else:
        lists = request.user.company

    list_count = lists.count()

    if request.user.is_staff:
        task_count = Task.objects.filter(completed=False).count()
    else:
        task_count = (
            Task.objects.filter(completed=False)
            .filter(task_list=request.user.company)
            .count()
        )

    context = {
        'lists': lists,
        'searchform': searchform,
        'list_count': list_count,
        'task_count': task_count,
    }
    # print('list_lists', context)

    return render(request, 'ticket/list_lists.html', context)
