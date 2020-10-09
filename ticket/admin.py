from django.contrib import admin

from ticket.models import Attachment, Comment, Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_list', 'assigned_to', 'completed', 'completed_date', 'credits_comsumed')
    list_filter = ('task_list', 'assigned_to', 'completed')
    # ordering = ('priority',)
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'snippet')


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'added_by', 'timestamp', 'file')
    autocomplete_fields = ['added_by', 'task']


admin.site.register(Comment, CommentAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Attachment, AttachmentAdmin)
