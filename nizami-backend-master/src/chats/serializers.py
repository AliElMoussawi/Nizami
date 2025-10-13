from django.http import Http404
from rest_framework import serializers

from src.chats.flow import build_graph
from src.chats.models import Chat, Message, MessageFile
from src.chats.utils import truncate_to_complete_words

from src.ledger.services import pre_message_processing_validate, decrement_credits_post_message


class CreateChatSerializer(serializers.Serializer):
    first_text_message = serializers.CharField(required=True, write_only=True)

    def create(self, validated_data):
        user = self.context['request'].user

        return Chat.objects.create(
            user=user,
            title=truncate_to_complete_words(validated_data['first_text_message']),
        )


class UpdateChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['title']


class CreateMessageFileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, allow_empty_file=False, allow_null=False)

    def create(self, validated_data):
        user = self.context['request'].user

        return MessageFile.objects.create(
            user=user,
            **validated_data,
        )


class ListChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at']


class ListMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'uuid', 'chat_id', 'text', 'created_at', 'role', 'messageFiles',
                  'translation_disclaimer_language', 'show_translation_disclaimer', 'language']
        depth = 1

    chat_id = serializers.PrimaryKeyRelatedField(read_only=True)


class ListMessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = ["id", "file_name", "extension", "size", 'created_at']


class CreateMessageSerializer(serializers.Serializer):
    uuid = serializers.CharField(required=True)
    chat_id = serializers.IntegerField(required=True)
    text = serializers.CharField(required=True)
    message_file_ids = serializers.ListField(required=False, allow_null=True, child=serializers.IntegerField())
    messageFiles = ListMessageFileSerializer(many=True, required=False, read_only=True)
    show_translation_disclaimer = serializers.BooleanField(required=False)
    translation_disclaimer_language = serializers.CharField(required=False)
    language = serializers.CharField(required=False, read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        chat_id = validated_data.get('chat_id')
        
        user, subcription =pre_message_processing_validate(user=user)
        graph = build_graph()

        # validate chat access for current user
        chat = Chat.objects.get(user=user, id=chat_id)
        if chat is None:
            raise Http404

        output = graph.invoke({
            'input': validated_data['text'],
            'uuid': validated_data['uuid'],
            'chat_id': chat_id,
        })
        decrement_credits_post_message(user=user, subscription=subcription)
        return output['system_message']
