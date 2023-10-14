from django.contrib import admin

from ..models import Tariff


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'partner',
        'name',
        'max_clients',
        'max_templates',
        'payment',
        'discounts',
    )

    list_filter = (
        'is_use_push_for_geolocation',
        'is_use_api',
        'is_use_sms',
        'is_use_sending_cards_by_sms',
        'is_personal_manager',
        'is_importing_client_database',
        'is_white_label',
        'updated_at',
        'created_at',
    )

    search_fields = ('name',)
    readonly_fields = ('partner', 'updated_at', 'created_at',)
    filter_horizontal = ('permissions',)

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
                'name',
                'permissions',
                'max_clients',
                'cost_additional_client',
                'max_templates',
                'payment',
                'discounts',
                'is_personal_manager',
                'is_importing_client_database',
                'is_white_label',
            )
        }),
        ('PUSH', {
            'fields': (
                'is_use_push_for_geolocation',
                'push_limits',
            )
        }),
        ('API', {
            'fields': (
                'is_use_api',
                'api_requests_limits',
            )
        }),
        ('SMS', {
            'fields': (
                'is_use_sms',
                'is_use_sending_cards_by_sms',
                'cost_sms_message',
            )
        }),
        ('Верификации звонком', {
            'fields': (
                'cost_of_verification_by_call',
                'count_verifications_included_in_the_price',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
