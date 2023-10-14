from django.contrib import admin

from ..models import Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'codename', 'is_partners',)
    search_fields = ('name', 'codename',)
    list_filter = ('is_partners',)
