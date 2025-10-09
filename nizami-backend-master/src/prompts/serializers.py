from rest_framework import serializers

from src.prompts.models import Prompt


class UpdatePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['value']


class ListPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = '__all__'
