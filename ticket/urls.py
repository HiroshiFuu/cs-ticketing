from django.conf import settings
from django.urls import path

from ticket import views
from ticket.features import HAS_TASK_MERGE

app_name = 'ticket'

urlpatterns = [
    path('lists', views.list_lists, name='lists'),
    # Allow users to post tasks from outside cs-support-ticket (e.g. for filing tickets - see docs)
    path('add/', views.external_add, name='external_add'),
    # View tickets created by external users
    # path('external_mine/', views.list_detail, {'list_slug': 'mine'}, name='external_mine'),
    path('', views.my_list_detail),
    path('mine/', views.my_list_detail, name='mine'),
    path(
        'mine/completed',
        views.my_list_detail,
        {'view_completed': True},
        name='mine_completed'
    ),
    path('company/<int:company_id>/', views.list_detail, name='list_detail'),
    path(
        'company/<int:company_id>/completed',
        views.list_detail,
        {'view_completed': True},
        name='list_detail_completed',
    ),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path(
        'attachment/remove/<int:attachment_id>/', views.remove_attachment, name='remove_attachment'
    ),
]

if HAS_TASK_MERGE:
    # ensure mail tracker autocomplete is optional
    from ticket.views.task_autocomplete import TaskAutocomplete

    urlpatterns.append(
        path(
            'task/<int:task_id>/autocomplete/', TaskAutocomplete.as_view(), name='task_autocomplete'
        )
    )

urlpatterns.extend(
    [
        path('toggle_done/<int:task_id>/',
             views.toggle_done, name='task_toggle_done'),
        path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
        path('search/', views.search, name='search'),
    ]
)
