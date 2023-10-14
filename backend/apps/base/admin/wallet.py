from django.contrib import admin

from ..forms import WalletAdminForm
from ..models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    form = WalletAdminForm

    list_display = (
        'id',
        'partner',
        'uuid',
        'name',
        'snumbers',
        'type',
        'cert',
        'expires_at',
        'deleted_at',
    )

    list_filter = (
        'type',
        'is_use_welcome_bonuses',
        'is_immediately_transfer_bonuses',
        'is_burn_bonuses',
        'is_use_push_for_geolocation',
        'is_unlimited',
        'is_message_about_bonus_received_displayed',
        'expires_at',
        'deleted_at',
        'updated_at',
        'created_at',
    )

    fieldsets = (
        ('Партнер', {
            'fields': (
                'partner',
            )
        }),
        ('Информация', {
            'fields': (
                'uuid',
                'name',
                'snumbers',
                'type',
                'cert',
            )
        }),
        ('Скидочная карта', {
            'fields': (
                'discount',
            )
        }),
        ('Бонусная карта', {
            'fields': (
                'cashback',
                'conversion',
                'is_use_welcome_bonuses',
                'bonuses',
                'is_immediately_transfer_bonuses',
                'min_expenditure_obtaining_bonuses',
                'is_burn_bonuses',
                'validity_period_of_bonuses',
            )
        }),
        ('Чоп-карта', {
            'fields': (
                'stamps',
                'active_stamp_icon',
                'nonactive_stamp_icon',
                'finish_stamp_icon',
                'is_unlimited',
                'is_message_about_bonus_received_displayed',
                'expires_at',
            )
        }),
        ('Геолокация', {
            'fields': (
                'is_use_push_for_geolocation',
                'geolocations',
            )
        }),
        ('Внешний вид карты', {
            'fields': (
                'icon',
                'logotype',
                'background_image',
                'frontend',
                'backend',
            )
        }),
        ('Мягкое удаление', {
            'fields': (
                'is_delete',
                'deleted_at',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    search_fields = ('name', 'snumbers',)
    readonly_fields = ('uuid', 'deleted_at', 'updated_at', 'created_at',)
