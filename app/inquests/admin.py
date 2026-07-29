from django.contrib import admin

from .models import Inquest, InquestDocument, Deceased, RecommendationRecipient, InquestKeyword, PresidingOfficer, \
    CauseOfDeath


@admin.register(Inquest)
class InquestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'display_name',
        'overview',
    )
    search_fields = (
        'name',
        'overview',
        'summary',
        'key_case_reason',
    )
    filter_horizontal = ('keywords',)

    @admin.display(description='name')
    def display_name(self, obj: Inquest) -> str:
        return str(obj)


@admin.register(InquestDocument)
class InquestDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'date',
        'inquest',
    )
    search_fields = (
        'name',
        'source',
    )
    list_filter = ('date',)
    ordering = ('-date',)
    autocomplete_fields = ('inquest',)


@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'middle_name',
        'last_name',
        'date_of_death',
        'inquest',
    )
    search_fields = (
        'name',
        'cause',
        'manner',
    )
    list_filter = ('date_of_death', 'sex')
    ordering = ('-date_of_death',)
    autocomplete_fields = ('inquest',)


@admin.register(CauseOfDeath)
class CauseOfDeathAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )
    search_fields = (
        'name',
    )


@admin.register(RecommendationRecipient)
class RecommendationRecipientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )
    search_fields = (
        'name',
    )
    filter_horizontal = ('inquests',)


@admin.register(InquestKeyword)
class InquestKeywordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'description',
    )
    search_fields = ('name',)


@admin.register(PresidingOfficer)
class PresidingOfficerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
    )
    search_fields = ('first_name', 'last_name')
