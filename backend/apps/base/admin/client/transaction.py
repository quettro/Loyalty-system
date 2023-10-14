from django.contrib import admin

from ...models import ClientTransaction
from .bonus import BonusInlineAdmin


@admin.register(ClientTransaction)
class ClientTransactionAdmin(admin.ModelAdmin):
    inlines = (BonusInlineAdmin,)

    list_display = (
        'id',
        'client',
        'receipt',
        'amount',
        'percent',
    )

    list_filter = (
        'is_auto_add_bonuses',
        'updated_at',
        'created_at',
    )

    search_fields = (
        'client__name',
        'receipt',
        'message',
    )

    readonly_fields = (
        'updated_at',
        'created_at',
    )

    fieldsets = (
        (None, {
            'fields': (
                'client',
            )
        }),
        ('Информация', {
            'fields': (
                'receipt',
                'amount',
            )
        }),
        ('Доп. информация', {
            'fields': (
                'message',
            )
        }),
        ('Скидочная карта / Бонусная карта', {
            'fields': (
                'percent',
            )
        }),
        ('Бонусная карта', {
            'fields': (
                'is_auto_add_bonuses',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )

    def has_change_permission(self, *args, **kwargs):
        return False


class ClientTransactionInlineAdmin(admin.TabularInline):
    model = ClientTransaction
    extra = 1
    show_change_link = True

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False
