from django.contrib import admin

from ...models import Client, Reward, Wallet


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'type',
        'count',
    )

    list_filter = (
        'type',
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
                'type',
                'count',
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'client' in db_field.name:
            kwargs['queryset'] = Client.objects.filter(
                wallet__type=Wallet.Type.CHOP)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RewardInlineAdmin(admin.TabularInline):
    model = Reward
    extra = 1
    show_change_link = True

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False
