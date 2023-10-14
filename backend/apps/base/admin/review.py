from django.contrib import admin

from ..models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'ip',
        'rating',
    )

    list_filter = (
        'rating',
        'updated_at',
        'created_at',
    )

    search_fields = ('ip', 'message',)
    readonly_fields = ('updated_at', 'created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'client',
            )
        }),
        ('Информация', {
            'fields': (
                'ip',
                'message',
                'rating',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
