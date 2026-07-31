from django.contrib import admin

from .models import Inquest, InquestDocument, Deceased, InquestKeyword, Participant, Role, \
    CauseOfDeath, InquestGroup, PartyType, Party


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
    filter_horizontal = ('keywords', 'groups', 'recommendation_recipients')

    @admin.display(description='name')
    def display_name(self, obj: Inquest) -> str:
        return str(obj)


@admin.register(InquestDocument)
class InquestDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'document_type',
        'date',
        'inquest',
    )
    search_fields = (
        'name',
        'source',
    )
    list_filter = ('date', 'document_type')
    ordering = ('-date',)
    autocomplete_fields = ('inquest',)


@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'age',
        'cause',
        'manner',
        'inquest',
    )
    search_fields = (
        'first_name',
        'last_name',
        'cause__name',
        'manner',
    )
    list_filter = ('cause', 'manner')
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


@admin.register(PartyType)
class InquestPartyTypeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
    )
    search_fields = ('name',)


@admin.register(Party)
class InquestRecipientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'party_type',
        'also_known_as',
    )
    search_fields = (
        'name',
        'also_known_as',
    )
    list_filter = ('party_type',)


@admin.register(InquestKeyword)
class InquestKeywordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'description',
    )
    search_fields = ('name',)


@admin.register(InquestGroup)
class InquestGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'notes',
    )
    search_fields = ('name',)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
    )
    search_fields = ('first_name', 'last_name')
    filter_horizontal = ('roles',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
    )
    search_fields = ('name',)
    list_filter = ('category',)
