from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import GroupAdmin

from .models import Company
from .models import AuthUser
from .models import AuthGroup

import copy


admin.site.unregister(Group)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'credits',
        'subscription_based'
    ]


@admin.register(AuthGroup)
class AuthGroupAdmin(GroupAdmin):
    list_display = ['name', 'list_permissions']

    def list_permissions(self, obj):
        return ' | '.join([o.name for o in obj.permissions.all()])

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name in [*self.filter_horizontal]:
            form_field.widget.attrs={'size': '10'}
        return form_field


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    list_display = ['company', 'username', 'email', 'is_active']
    ordering = ('username',)
    list_display_links = ('username', 'email')
    fieldsets = (
        (None, {'fields': ['username', 'email', 'company']}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': [
         'groups', 'is_staff', 'is_active', 'password']}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ['username', 'email', 'company', 'password1', 'password2', 'is_staff']}
         ),
    )

    def get_list_display(self, request):
        list_display = copy.deepcopy(self.list_display)
        if not request.user.is_superuser:
            list_display.pop(0)
        return list_display

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(company=request.user.company)

    def get_fieldsets(self, request, obj=None):
        if obj:
            if request.user.is_superuser:
                fieldsets = copy.deepcopy(self.fieldsets)
            else:
                fieldsets = (
                    (None, {'fields': ['email']}),
                    ('Permissions', {'fields': ['password']}),
                )
        else:
            fieldsets = copy.deepcopy(self.add_fieldsets)
            # if request.user.is_superuser:
            #     fieldsets = copy.deepcopy(self.add_fieldsets)
            #     self.add_form = CustomCompanyCreationForm
            # else:
            #     self.add_form = CustomUserCreationForm
            #     # fieldsets[0][1]['fields'].pop(-1)
            #     fieldsets[0][1]['fields'] = ['username', 'email', 'password1', 'password2']
        # print('get_fieldsets', fieldsets)
        return fieldsets