from django.contrib import admin

from .models import Authority, AuthorityDocument, AuthorityKeyword, AuthorityGroup


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'overview',
        'jurisdiction'
    )
    search_fields = (
        'name',
        'overview',
        'summary',
        'notes',
        'quotes',
        'key_case_reason',
    )
    list_filter = ('jurisdiction',)
    ordering = ('name',)
    autocomplete_fields = ('authority_citations', 'authority_related')
    filter_horizontal = ('keywords', 'groups')


@admin.register(AuthorityDocument)
class AuthorityDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'document_type',
        'source',
        'date',
        'authority',
    )
    search_fields = (
        'name',
        'source',
    )
    list_filter = ('document_type',)
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


@admin.register(AuthorityGroup)
class AuthorityGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'notes',
    )
    search_fields = ('name',)
