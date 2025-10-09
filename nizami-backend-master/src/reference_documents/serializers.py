from django.db import transaction, connection
from django_q.tasks import async_task
from rest_framework import serializers

from src.reference_documents.models import ReferenceDocument
from src.reference_documents.tasks import analyze_reference_document
from src.reference_documents.utils import generate_description_for_ref_doc
from src.settings import embeddings


class CreateReferenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceDocument
        fields = ['file', 'name', 'language', 'description']

    file = serializers.FileField(required=True, allow_empty_file=False, allow_null=False)
    name = serializers.CharField(required=True, allow_null=False)
    language = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate_name(self, value):
        if ReferenceDocument.objects.filter(name=value).exists():
            raise serializers.ValidationError("The file name already exists")
        return value

    def create(self, validated_data):
        document: ReferenceDocument = ReferenceDocument.objects.create(**validated_data,
                                                                       created_by=self.context['request'].user)

        async_task(analyze_reference_document, document.id)

        return document


class UpdateReferenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceDocument
        fields = ['name', 'description', 'language']

    name = serializers.CharField(required=True, allow_null=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        new_language = validated_data.get('language', instance.language)
        old_language = instance.language

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', None)

        if instance.description in [None, '']:
            instance.description = generate_description_for_ref_doc(instance)
            instance.description_embedding = embeddings.embed_query(instance.description)

        instance.language = new_language.lower()
        instance.save()

        if not old_language or new_language.lower() != old_language.lower():
            sql = """
                UPDATE langchain_pg_embedding
                SET cmetadata = jsonb_set(COALESCE(cmetadata, '{}'), '{language}', %s, true)
                WHERE cmetadata->>'reference_document_id' = '%s'
                ;
            """
            with connection.cursor() as cursor:
                cursor.execute(sql, [f'"{new_language.lower()}"', instance.id])

        return instance


class ListReferenceDocumentSerializer(serializers.ModelSerializer):
    created_by_full_name = serializers.SerializerMethodField()

    class Meta:
        model = ReferenceDocument
        fields = ["id", "name", "description", "extension", "size", 'status', 'created_at', 'created_by_full_name',
                  'updated_at',
                  'language', 'file_name']

    def get_created_by_full_name(self, obj):
        if obj.created_by is None:
            return None

        return f"{obj.created_by.first_name} {obj.created_by.last_name}"
