from django.contrib import admin

from ..models import Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'wallet',
        'name',
        'percent',
        'expenses',
        'visits',
        'number_of_days_with_us',
        'is_by_default',
    )

    list_filter = (
        'is_by_default',
        'updated_at',
        'created_at',
    )

    search_fields = ('name',)
    readonly_fields = ('updated_at', 'created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'wallet',
            )
        }),
        ('Информация', {
            'fields': (
                'name',
                'percent',
                'expenses',
                'visits',
                'number_of_days_with_us',
                'is_by_default',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
