from django.contrib import admin

from ..models import Trigger


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'wallet',
        'audience',
        'name',
        'description',
        'launch_at',
        'created_at',
    )

    list_filter = (
        'is_send_push_notifications',
        'is_add_bonuses',
        'is_increased_percentage',
        'is_repeat_every_year',
        'launch_at',
        'updated_at',
        'created_at',
    )

    search_fields = ('name', 'description',)
    readonly_fields = ('updated_at', 'created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'wallet',
                'audience',
            )
        }),
        ('Информация', {
            'fields': (
                'name',
                'description',
                'icon',
            )
        }),
        ('Пуш уведомления', {
            'fields': (
                'is_send_push_notifications',
                'message_for_push_notifications',
            )
        }),
        ('Баллы', {
            'fields': (
                'is_add_bonuses',
                'bonuses',
            )
        }),
        ('Повышенный кэшбэк/скидка', {
            'fields': (
                'is_increased_percentage',
                'percent',
                'days_before_the_event',
                'days_after_the_event',
            )
        }),
        ('Запуск', {
            'fields': (
                'is_repeat_every_year',
                'launch_at',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
