from django.http import Http404
from rest_framework import serializers
import logging

from src.chats.flow import build_graph
from src.chats.models import Chat, Message, MessageFile
from src.chats.utils import truncate_to_complete_words

from src.ledger.services import pre_message_processing_validate, decrement_credits_post_message

logger = logging.getLogger(__name__)


ALLOWED_MESSAGE_FILE_EXTENSIONS = {"pdf", "doc", "docx"}
ALLOWED_MESSAGE_FILE_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_MESSAGE_FILE_SIZE_BYTES = 25 * 1024 * 1024


def validate_message_file(*, uploaded_file):
    """
    Validate uploaded message file for size and type.
    """
    if uploaded_file.size > MAX_MESSAGE_FILE_SIZE_BYTES:
        raise serializers.ValidationError("File is too large.")

    file_name = getattr(uploaded_file, "name", "") or ""
    extension = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    content_type = getattr(uploaded_file, "content_type", "") or ""

    if extension not in ALLOWED_MESSAGE_FILE_EXTENSIONS and content_type not in ALLOWED_MESSAGE_FILE_CONTENT_TYPES:
        raise serializers.ValidationError("Unsupported file type.")
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

    def validate_file(self, value):
        validate_message_file(uploaded_file=value)
        return value


class ListChatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at']


class ListMessagesSerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'uuid', 'chat_id', 'text', 'created_at', 'role', 'messageFiles',
                  'attachments',
                  'translation_disclaimer_language', 'show_translation_disclaimer', 'language']
        depth = 1

    chat_id = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_attachments(self, obj):
        # MessageAttachment -> uploads.File (prefetch message_attachments__file in view)
        files = [ma.file for ma in obj.message_attachments.all()]
        return MessageAttachmentFileSerializer(files, many=True).data


class ListMessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = ["id", "file_name", "extension", "size", 'created_at']


class MessageAttachmentFileSerializer(serializers.Serializer):
    """Read-only summary of an uploads.File linked via MessageAttachment (for list API)."""
    id = serializers.UUIDField()
    file_name = serializers.CharField(source="original_filename")
    size = serializers.IntegerField(source="size_bytes")


class CreateMessageSerializer(serializers.Serializer):
    uuid = serializers.CharField(required=True)
    chat_id = serializers.IntegerField(required=True)
    text = serializers.CharField(required=True)
    message_file_ids = serializers.ListField(required=False, allow_null=True, child=serializers.IntegerField())
    attachment_file_ids = serializers.ListField(required=False, allow_null=True, child=serializers.UUIDField())
    intent = serializers.ChoiceField(required=False, allow_blank=True, choices=["SUMMARY", "QA"])
    messageFiles = ListMessageFileSerializer(many=True, required=False, read_only=True)
    show_translation_disclaimer = serializers.BooleanField(required=False)
    translation_disclaimer_language = serializers.CharField(required=False)
    language = serializers.CharField(required=False, read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        chat_id = validated_data.get('chat_id')
        message_file_ids = validated_data.get('message_file_ids') or []
        attachment_file_ids = validated_data.get('attachment_file_ids') or []
        intent = validated_data.get('intent') or None
        if intent == "":
            intent = None

        pre_message_processing_validate(user=user)
        chat = Chat.objects.get(user=user, id=chat_id)
        if chat is None:
            raise Http404

        if attachment_file_ids:
            from src.chats.attachment_flow import run_attachment_message_flow
            attachment_file_ids_str = [str(f) for f in attachment_file_ids]
            system_message = run_attachment_message_flow(
                user=user,
                chat_id=chat_id,
                text=validated_data['text'],
                message_uuid=validated_data['uuid'],
                attachment_file_ids=attachment_file_ids_str,
                intent=intent,
            )
            decrement_credits_post_message(user=user)
            return system_message

        graph = build_graph()
        output = graph.invoke({
            'input': validated_data['text'],
            'uuid': validated_data['uuid'],
            'chat_id': chat_id,
        })
        is_credits_decremented = decrement_credits_post_message(user=user)
        logger.info(f"Are credits decremented post message : {is_credits_decremented}")
        system_message = output['system_message']

        if message_file_ids:
            user_message = Message.objects.filter(uuid=validated_data['uuid']).first()
            if user_message is not None:
                MessageFile.objects.filter(
                    id__in=message_file_ids,
                    user=user,
                    message__isnull=True,
                ).update(message=user_message)

        return system_message
