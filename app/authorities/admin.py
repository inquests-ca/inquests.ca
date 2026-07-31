from django.contrib import admin

from .models import Authority, AuthorityDocument, AuthorityKeyword, AuthorityGroup, AuthorityLevel


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'overview',
        'jurisdiction',
        'level',
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
    autocomplete_fields = ('citations',)
    filter_horizontal = ('keywords', 'groups')


@admin.register(AuthorityDocument)
class AuthorityDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'document_type',
        'source',
        'citation',
        'is_primary',
        'level',
        'jurisdiction',
        'date',
        'authority',
    )
    search_fields = (
        'name',
        'source',
        'citation',
    )
    list_filter = ('document_type', 'level', 'jurisdiction', 'is_primary')
    ordering = ('-date',)
    autocomplete_fields = ('authority',)


@admin.register(AuthorityLevel)
class AuthorityLevelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'rank',
    )
    search_fields = ('name',)
    ordering = ('-rank',)


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
