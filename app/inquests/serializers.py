from rest_framework import serializers

from .models import Deceased, Inquest, InquestDocument


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


class InquestDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    jurisdiction = serializers.StringRelatedField()
    presiding_officer = serializers.StringRelatedField()
    keywords = serializers.StringRelatedField(many=True)
    groups = serializers.StringRelatedField(many=True)
    recommendation_recipients = serializers.StringRelatedField(many=True)
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
            'documents',
            'deceased',
        ]

    def get_display_name(self, obj):
        return str(obj)
