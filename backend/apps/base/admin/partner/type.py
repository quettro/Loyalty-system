from django.contrib import admin

from ...models import PartnerType


@admin.register(PartnerType)
class PartnerTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
