from django.contrib import admin

from ...models import ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'name')
    list_filter = ('updated_at', 'created_at',)
    search_fields = ('name',)
    readonly_fields = ('updated_at', 'created_at',)

    fieldsets = (
        ('Карта партнера', {
            'fields': (
                'wallet',
            )
        }),
        ('Информация', {
            'fields': (
                'name',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
