from django.contrib import admin

from ...forms import ClientAdminForm
from ...models import Client
from ..registration import RegistrationInlineAdmin
from .bonus import BonusInlineAdmin
from .percent import IncreasedPercentageInlineAdmin
from .reward import RewardInlineAdmin
from .stamp import StampInlineAdmin
from .transaction import ClientTransactionInlineAdmin


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm

    list_display = (
        'id',
        'partner',
        'wallet',
        'numbers',
        'name',
        'sex',
        'birthday',
        'phone',
        'deleted_at',
    )

    list_filter = (
        'sex',
        'is_welcome_bonuses_received',
        'deleted_at',
        'updated_at',
        'created_at',
    )

    readonly_fields = (
        'authentication_token',
        'numbers',
        'balance',
        'c_stamps',
        'a_stamps',
        'a_rewards',
        'pkpass',
        'updated_at',
        'created_at',
    )

    inlines = (
        IncreasedPercentageInlineAdmin,
        RegistrationInlineAdmin,
        RewardInlineAdmin,
        StampInlineAdmin,
        BonusInlineAdmin,
        ClientTransactionInlineAdmin,
    )

    fieldsets = (
        ('Партнер', {
            'fields': (
                'partner',
            )
        }),
        ('Карта', {
            'fields': (
                'wallet',
                'status',
            )
        }),
        ('Идентификация', {
            'fields': (
                'authentication_token',
            )
        }),
        ('Информация', {
            'fields': (
                'numbers',
                'name',
                'sex',
                'birthday',
                'phone',
            )
        }),
        ('Бонусная карта', {
            'fields': (
                'balance',
                'is_welcome_bonuses_received',
            )
        }),
        ('Чоп-карта', {
            'fields': (
                'c_stamps',
                'a_stamps',
                'a_rewards',
            )
        }),
        ('PkPass', {
            'fields': (
                'pkpass',
                'is_update_pkpass',
            )
        }),
        ('Важные даты', {
            'fields': (
                'deleted_at',
                'updated_at',
                'created_at',
            )
        }),
    )

    search_fields = ('numbers', 'name', 'phone',)
