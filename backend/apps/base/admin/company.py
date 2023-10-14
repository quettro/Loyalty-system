from django.contrib import admin

from ..models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'city',
        'name',
        'inn',
        'bik',
        'rs',
        'ks',
    )

    list_filter = ('updated_at', 'created_at',)
    readonly_fields = ('updated_at', 'created_at',)

    search_fields = (
        'city__name',
        'name',
        'inn',
        'bik',
        'rs',
        'ks',
        'yur_address',
        'fact_address',
    )

    fieldsets = (
        ('Компания', {
            'fields': (
                'city',
                'name',
                'inn',
                'bik',
                'rs',
                'ks',
                'yur_address',
                'fact_address',
            )
        }),
        ('Важные даты', {
            'fields': (
                'updated_at',
                'created_at',
            )
        }),
    )
