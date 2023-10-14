from django.contrib import admin

from ...models import Bonus, Client, ClientTransaction, Wallet


@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'transaction',
        'type',
        'count',
        'is_burned_bonuses',
        'expires_at',
    )

    list_filter = (
        'type',
        'is_burned_bonuses',
        'expires_at',
        'updated_at',
        'created_at',
    )

    readonly_fields = (
        'updated_at',
        'created_at',
    )

    search_fields = ('client__name',)

    fieldsets = (
        ('Информация', {
            'fields': (
                'client',
                'transaction',
                'type',
                'count',
                'message',
            )
        }),
        ('Срок действия', {
            'fields': (
                'is_burned_bonuses',
                'expires_at',
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'client' in db_field.name:
            kwargs['queryset'] = Client.objects.filter(
                wallet__type=Wallet.Type.BONUS)
        if 'transaction' in db_field.name:
            kwargs['queryset'] = ClientTransaction.objects.filter(
                client__wallet__type=Wallet.Type.BONUS)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BonusInlineAdmin(admin.TabularInline):
    model = Bonus
    extra = 1
    show_change_link = True

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False
