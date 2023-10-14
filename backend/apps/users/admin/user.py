from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ..forms import CustomUserChangeForm, CustomUserCreationForm
from ..models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        'id',
        'email',
        'first_name',
        'last_name',
        'patronymic',
        'phone',
        'is_staff',
        'is_superuser',
        'is_active',
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'last_login',
        'date_joined',
    )

    fieldsets = (
        ('Информация', {
            'fields': (
                'email',
                'password',
                'first_name',
                'last_name',
                'patronymic',
                'phone',
            )
        }),
        ('Разрешения', {
            'fields': (
                'groups',
                'user_permissions',
                'is_staff',
                'is_superuser',
                'is_active',
            )
        }),
        ('Важные даты', {
            'fields': (
                'last_login',
                'date_joined',
            )
        })
    )

    add_fieldsets = (
        (None, {
            'classes': (
                'wide',
            ),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'patronymic',
                'phone',
                'is_staff',
                'is_superuser',
                'is_active'
            )
        }),
    )

    ordering = ('-id',)
    search_fields = ('email', 'first_name', 'last_name', 'phone',)
