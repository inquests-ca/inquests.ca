from django.contrib import admin

from .models import Authority, AuthorityDocument, AuthorityKeyword


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'overview',
    )
    search_fields = (
        'name',
        'overview',
        'summary',
        'notes',
        'quotes',
        'key_case_reason',
    )
    ordering = ('name',)
    autocomplete_fields = ('authority_citations', 'authority_related')
    filter_horizontal = ('keywords',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'overview',
                'summary',
            )
        }),
        ('Additional details', {
            'fields': ('notes', 'quotes', 'key_case_reason'),
        }),
        ('Relations', {
            'fields': ('authority_citations', 'authority_related'),
        }),
    )


@admin.register(AuthorityDocument)
class AuthorityDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'date',
        'authority',
    )
    search_fields = (
        'name',
        'source',
    )
    list_filter = ('date',)
    ordering = ('-date',)
    autocomplete_fields = ('authority',)


@admin.register(AuthorityKeyword)
class AuthorityKeywordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'description',
    )
    search_fields = ('name',)
