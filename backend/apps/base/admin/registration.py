from django.contrib import admin

from ..models import Registration


class RegistrationInlineAdmin(admin.TabularInline):
    model = Registration
    extra = 1
    show_change_link = True

    fields = (
        'device_library_id',
        'push_token',
        'os_family',
        'os_version',
        'device_family',
        'device_brand',
        'device_model',
    )

    readonly_fields = fields

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'device_library_id',
        'os_family',
        'os_version',
        'device_family',
        'device_brand',
        'device_model',
    )

    list_filter = (
        'os_family',
        'updated_at',
        'created_at',
    )

    search_fields = (
        'device_library_id',
        'push_token',
        'os_family',
        'os_version',
        'device_family',
        'device_brand',
        'device_model',
    )

    fieldsets = (
        ('Клиент', {
            'fields': (
                'client',
            )
        }),
        ('Идентификация', {
            'fields': (
                'device_library_id',
                'push_token',
            )
        }),
        ('Устройство', {
            'fields': (
                'os_family',
                'os_version',
                'device_family',
                'device_brand',
                'device_model',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
