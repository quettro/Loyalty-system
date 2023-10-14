from django.contrib import admin

from ..models import Verification


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'partner',
        'token',
        'phone',
        'code',
        'status',
        'is_used',
    )

    list_filter = (
        'status',
        'is_used',
        'updated_at',
        'created_at',
    )

    search_fields = ('phone', 'code',)
    readonly_fields = ('token', 'updated_at', 'created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'partner',
            )
        }),
        ('Информация', {
            'classes': (
                'wide',
            ),
            'fields': (
                'token',
                'phone',
                'smsc_id',
                'code',
                'status',
                'is_used',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
