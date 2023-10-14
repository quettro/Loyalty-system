from django.contrib import admin

from ...models import PartnerTransaction


@admin.register(PartnerTransaction)
class PartnerTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'partner',
        'type',
        'amount',
        'balance',
    )

    list_filter = (
        'type',
        'updated_at',
        'created_at',
    )

    search_fields = (
        'message',
    )

    readonly_fields = (
        'balance',
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
                'type',
                'amount',
                'balance',
                'message',
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


class PartnerTransactionInlineAdmin(admin.TabularInline):
    model = PartnerTransaction
    extra = 1
    show_change_link = True
    readonly_fields = ('balance',)
    fields = ('type', 'amount', 'balance', 'message',)

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False
