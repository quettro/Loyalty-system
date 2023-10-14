from django.contrib import admin
from django.contrib.auth import get_user_model

from ..models import Employee, Permission

User = get_user_model()


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'partner',
        'pincode',
    )

    filter_horizontal = ('permissions',)
    list_filter = ('updated_at', 'created_at',)
    search_fields = ('pincode',)
    readonly_fields = ('updated_at', 'created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'partner',
            )
        }),
        ('Информация', {
            'fields': (
                'permissions',
                'pincode',
                'note',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'user' in db_field.name:
            kwargs['queryset'] = User.objects.filter(partner=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if 'permissions' in db_field.name:
            kwargs['queryset'] = Permission.objects.filter(is_partners=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
