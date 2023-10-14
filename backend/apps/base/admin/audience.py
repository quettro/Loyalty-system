from django.contrib import admin

from ..models import Audience


@admin.register(Audience)
class AudienceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'wallet',
        'name',
        'sex',
        'device',
        'is_visited_the_institution',
    )

    list_filter = (
        'is_use_age',
        'is_use_birthday',
        'is_use_days_from_registration',
        'is_use_average_check',
        'is_use_visits',
        'sex',
        'device',
        'is_visited_the_institution',
        'updated_at',
        'created_at',
    )

    readonly_fields = (
        'updated_at',
        'created_at',
    )

    fieldsets = (
        ('Информация', {
            'fields': (
                'wallet',
                'name',
            )
        }),
        ('Возраст', {
            'fields': (
                'is_use_age',
                'min_age',
                'max_age',
            )
        }),
        ('День рождения', {
            'fields': (
                'is_use_birthday',
                'min_birthday',
                'max_birthday',
            )
        }),
        ('Кол-во дней с момента регистрации', {
            'fields': (
                'is_use_days_from_registration',
                'min_days_from_registration',
                'max_days_from_registration',
            )
        }),
        ('Средний чек', {
            'fields': (
                'is_use_average_check',
                'min_average_check',
                'max_average_check',
            )
        }),
        ('Кол-во визитов', {
            'fields': (
                'is_use_visits',
                'min_visits',
                'max_visits',
            )
        }),
        ('Другое', {
            'fields': (
                'sex',
                'device',
                'is_visited_the_institution',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    search_fields = ('name',)
