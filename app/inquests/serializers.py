from rest_framework import serializers

from .models import Deceased, Inquest, InquestDocument, Participant, Party, InquestKeyword


class InquestSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    jurisdiction = serializers.StringRelatedField()
    presiding_officer = serializers.StringRelatedField()

    class Meta:
        model = Inquest
        fields = [
            'id',
            'display_name',
            'jurisdiction',
            'presiding_officer',
            'start_date',
            'end_date',
            'overview',
            'key_case_reason',
        ]

    def get_display_name(self, obj):
        return str(obj)


class InquestDocumentSerializer(serializers.ModelSerializer):
    document_type = serializers.CharField(source='get_document_type_display')

    class Meta:
        model = InquestDocument
        fields = ['id', 'name', 'document_type', 'date', 'source', 'link']


class DeceasedSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    sex = serializers.CharField(source='get_sex_display')
    manner = serializers.CharField(source='get_manner_display')
    reason_for_inquest = serializers.CharField(source='get_reason_for_inquest_display', allow_null=True)
    inmate_type = serializers.CharField(source='get_inmate_type_display', allow_null=True)
    cause = serializers.StringRelatedField()

    class Meta:
        model = Deceased
        fields = [
            'id',
            'display_name',
            'age',
            'date_of_birth',
            'date_of_death',
            'sex',
            'manner',
            'reason_for_inquest',
            'inmate_type',
            'cause',
            'cause_description',
        ]

    def get_display_name(self, obj):
        return str(obj)


class PartyRecipientSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    inquest_count = serializers.SerializerMethodField()

    class Meta:
        model = Party
        fields = ['id', 'display_name', 'inquest_count']

    def get_display_name(self, obj):
        return str(obj)

    def get_inquest_count(self, obj):
        # obj.inquests is the reverse M2M back to Inquest -- this is a
        # separate, unscoped query from whatever prefetched `obj` itself, so
        # it correctly counts across *all* inquests, not just the one being
        # viewed. (An annotate()-inside-Prefetch() approach looks tempting
        # but is wrong here: Django reuses the same join for the prefetch's
        # own parent-scoping filter and a Count('inquests') annotation,
        # since both traverse the identical reverse relation, silently
        # collapsing the count down to just the current inquest.)
        return obj.inquests.count()


class InquestKeywordSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = InquestKeyword
        fields = ['id', 'display_name']

    def get_display_name(self, obj):
        return str(obj)


class ParticipantSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    roles = serializers.StringRelatedField(many=True)

    class Meta:
        model = Participant
        fields = ['id', 'display_name', 'roles']

    def get_display_name(self, obj):
        return str(obj)


class InquestDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    jurisdiction = serializers.StringRelatedField()
    presiding_officer = serializers.StringRelatedField()
    keywords = InquestKeywordSerializer(many=True)
    groups = serializers.StringRelatedField(many=True)
    recommendation_recipients = PartyRecipientSerializer(many=True)
    participants = ParticipantSerializer(many=True)
    documents = InquestDocumentSerializer(many=True)
    deceased = DeceasedSerializer(many=True)

    class Meta:
        model = Inquest
        fields = [
            'id',
            'display_name',
            'jurisdiction',
            'presiding_officer',
            'start_date',
            'end_date',
            'sitting_days',
            'recommendation_count',
            'response_to_recommendations',
            'overview',
            'summary',
            'key_case_reason',
            'keywords',
            'groups',
            'recommendation_recipients',
            'participants',
            'documents',
            'deceased',
        ]

    def get_display_name(self, obj):
        return str(obj)
