from django.contrib import admin

from ..models import CustomToken


@admin.register(CustomToken)
class CustomTokenAdmin(admin.ModelAdmin):
    list_display = (
        'key',
        'user',
        'ip',
        'browser_family',
        'os_family',
        'device_family',
        'created_at',
    )

    list_filter = (
        'browser_family',
        'os_family',
        'created_at',
    )

    readonly_fields = (
        'key',
        'ip',
        'browser_family',
        'browser_version',
        'os_family',
        'os_version',
        'device_family',
        'device_brand',
        'device_model',
        'created_at',
    )

    fieldsets = (
        (None, {
            'fields': (
                'user',
            )
        }),
        ('Устройство', {
            'fields': (
                'ip',
                'browser_family',
                'browser_version',
                'os_family',
                'os_version',
                'device_family',
                'device_brand',
                'device_model',
            )
        }),
        ('Важные даты', {
            'fields': (
                'created_at',
            )
        }),
    )

    search_fields = ('key',)
