from django.contrib import admin

from ...models import IncreasedPercentage


@admin.register(IncreasedPercentage)
class IncreasedPercentageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'percent',
        'activated_at',
        'expires_at',
    )

    list_filter = (
        'activated_at',
        'expires_at',
        'updated_at',
        'created_at',
    )

    readonly_fields = (
        'updated_at',
        'created_at',
    )

    search_fields = ('client__name',)

    fieldsets = (
        ('Информация', {
            'fields': (
                'client',
                'percent',
            )
        }),
        ('Срок действия', {
            'fields': (
                'activated_at',
                'expires_at',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )


class IncreasedPercentageInlineAdmin(admin.TabularInline):
    model = IncreasedPercentage
    extra = 1
    show_change_link = True
