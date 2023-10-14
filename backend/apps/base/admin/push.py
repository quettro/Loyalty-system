from django.contrib import admin

from ..models import Push


@admin.register(Push)
class PushAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'wallet',
        'audience',
        'name',
        'status',
        'is_send_immediately',
    )

    list_filter = (
        'status',
        'is_send_immediately',
        'send_at',
        'updated_at',
        'created_at',
    )

    fieldsets = (
        (None, {
            'fields': (
                'wallet',
                'audience',
            )
        }),
        ('Информация', {
            'fields': (
                'task_id',
                'name',
                'message',
                'status',
            )
        }),
        ('Отправка', {
            'fields': (
                'is_send_immediately',
                'send_at',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    search_fields = ('name', 'message',)
    readonly_fields = ('task_id', 'status', 'updated_at', 'created_at',)

    def has_change_permission(self, request, obj=None):
        return False
