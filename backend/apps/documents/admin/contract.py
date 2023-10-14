from django.contrib import admin

from ..forms import ContractAdminForm
from ..models import AcceptedContract, Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    form = ContractAdminForm

    list_display = (
        'id',
        'name',
        'version',
        'updated_at',
        'created_at',
    )

    list_filter = (
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
                'name',
                'version',
                'content',
                'is_reset_accepted_contracts',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    def has_add_permission(self, *args, **kwargs):
        _is = super().has_add_permission(*args, **kwargs)
        return Contract.objects.count() <= 0 if _is else _is


class AcceptedContractInlineAdmin(admin.TabularInline):
    model = AcceptedContract
    extra = 1
    show_change_link = True


@admin.register(AcceptedContract)
class AcceptedContractAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'partner',
        'contract',
        'ip',
        'browser_family',
        'os_family',
        'device_family',
        'created_at',
    )

    list_filter = (
        'browser_family',
        'os_family',
        'updated_at',
        'created_at',
    )

    readonly_fields = (
        'ip',
        'browser_family',
        'browser_version',
        'os_family',
        'os_version',
        'device_family',
        'device_brand',
        'device_model',
        'updated_at',
        'created_at',
    )

    fieldsets = (
        ('Информация', {
            'fields': (
                'partner',
                'contract',
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
                'updated_at',
                'created_at',
            )
        }),
    )
