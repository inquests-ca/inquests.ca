from rest_framework import serializers

from .models import Authority, AuthorityDocument


class AuthoritySerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    jurisdiction = serializers.StringRelatedField()

    class Meta:
        model = Authority
        fields = [
            'id',
            'display_name',
            'jurisdiction',
            'is_judicial_review',
            'overview',
            'key_case_reason',
        ]

    def get_display_name(self, obj):
        return str(obj)


class AuthorityDocumentSerializer(serializers.ModelSerializer):
    document_type = serializers.CharField(source='get_document_type_display')
    level = serializers.StringRelatedField()
    jurisdiction = serializers.StringRelatedField()

    class Meta:
        model = AuthorityDocument
        fields = [
            'id',
            'name',
            'document_type',
            'date',
            'source',
            'citation',
            'is_primary',
            'level',
            'jurisdiction',
            'link',
        ]


class AuthorityDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    jurisdiction = serializers.StringRelatedField()
    level = serializers.SerializerMethodField()
    keywords = serializers.StringRelatedField(many=True)
    groups = serializers.StringRelatedField(many=True)
    citations = serializers.StringRelatedField(many=True)
    cited_by = serializers.StringRelatedField(many=True)
    documents = AuthorityDocumentSerializer(many=True, source='document')

    class Meta:
        model = Authority
        fields = [
            'id',
            'display_name',
            'jurisdiction',
            'level',
            'is_judicial_review',
            'overview',
            'summary',
            'notes',
            'quotes',
            'key_case_reason',
            'keywords',
            'groups',
            'citations',
            'cited_by',
            'documents',
        ]

    def get_display_name(self, obj):
        return str(obj)

    def get_level(self, obj):
        return str(obj.level) if obj.level else None
