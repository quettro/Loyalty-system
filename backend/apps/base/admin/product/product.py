from django.contrib import admin

from ...models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'category',
        'name',
        'amount',
        'is_use_cashback',
        'is_show',
    )

    list_filter = (
        'is_use_cashback',
        'is_show',
        'updated_at',
        'created_at',
    )

    search_fields = ('name',)
    readonly_fields = ('updated_at', 'created_at',)

    fieldsets = (
        ('Информация', {
            'classes': (
                'wide',
            ),
            'fields': (
                'category',
                'name',
                'amount',
                'is_use_cashback',
                'is_show',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
