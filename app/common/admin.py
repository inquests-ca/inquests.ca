from django.contrib import admin

from common.models import Jurisdiction


@admin.register(Jurisdiction)
class JurisdictionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'code',
    )
    search_fields = ('name', 'code')
