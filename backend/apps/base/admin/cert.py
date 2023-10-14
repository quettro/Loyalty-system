from django.contrib import admin

from ..models import Cert


@admin.register(Cert)
class CertAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'partner',
        'name',
        'p12_organization_name',
        'p12_team_identifier',
        'p12_pass_type_identifier',
    )

    list_filter = (
        'p12_activated_at',
        'p12_expires_at',
        'updated_at',
        'created_at',
    )

    readonly_fields = (
        'p12_cert_pem',
        'p12_cert_key',
        'p12_organization_name',
        'p12_team_identifier',
        'p12_pass_type_identifier',
        'p12_activated_at',
        'p12_expires_at',
        'p12_days_left',
        'updated_at',
        'created_at',
    )

    fieldsets = (
        (None, {
            'fields': (
                'partner',
            )
        }),
        ('Информация', {
            'fields': (
                'name',
            )
        }),
        ('.p12', {
            'fields': (
                'p12_cert',
                'p12_password',
                'p12_cert_pem',
                'p12_cert_key',
                'p12_organization_name',
                'p12_team_identifier',
                'p12_pass_type_identifier',
                'p12_activated_at',
                'p12_expires_at',
                'p12_days_left',
            )
        }),
        ('.p8', {
            'fields': (
                'p8_cert',
                'p8_key',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    search_fields = ('name', 'p12_organization_name', 'p12_team_identifier',)

    def p12_days_left(self, obj):
        return '-' if obj.id is None else obj.p12_days_left

    p12_days_left.short_description = (
        'Оставшийся срок действия сертификата в днях')
