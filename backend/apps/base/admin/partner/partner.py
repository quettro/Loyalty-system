from apps.documents.admin import AcceptedContractInlineAdmin
from django.contrib import admin
from django.contrib.auth import get_user_model

from ...forms import PartnerAdminForm
from ...models import Partner
from .transaction import PartnerTransactionInlineAdmin

User = get_user_model()


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    form = PartnerAdminForm
    inlines = (AcceptedContractInlineAdmin, PartnerTransactionInlineAdmin,)

    list_display = (
        'id',
        'user',
        'type',
        'company',
        'place_name',
        'address',
        'balance',
        'locations',
        'tariff',
    )

    list_filter = (
        'type',
        'is_show_client_phones',
        'is_negative_balance',
        'debiting_subscription_fee',
        'updated_at',
        'created_at',
    )

    search_fields = (
        'place_name',
        'address',
    )

    readonly_fields = (
        'balance',
        'updated_at',
        'created_at',
    )

    fieldsets = (
        ('Партнер', {
            'fields': (
                'user',
                'type',
                'company',
                'balance',
                'locations',
                'debiting_subscription_fee',
                'is_show_client_phones',
            )
        }),
        ('Тариф', {
            'fields': (
                'tariff',
                'is_individual_tariff',
            )
        }),
        ('Заведение', {
            'fields': (
                'place_name',
                'address',
            )
        }),
        ('Отрицательный баланс', {
            'fields': (
                'is_negative_balance',
                'limit_negative_balance',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'user' in db_field.name:
            kwargs['queryset'] = User.objects.filter(employee=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
