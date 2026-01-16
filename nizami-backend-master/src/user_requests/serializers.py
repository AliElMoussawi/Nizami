from rest_framework import serializers

from src.chats.serializers import ListChatsSerializer
from src.user_requests.models import LegalAssistanceRequest
from src.users.serializers import UserSerializer


class CreateLegalAssistanceRequestSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField(required=True)
    
    def validate_chat_id(self, value):
        """Validate that the chat exists and belongs to the user"""
        user = self.context['request'].user
        from src.chats.models import Chat
        try:
            chat = Chat.objects.get(id=value, user=user)
            # Check if chat has at least 2 messages
            from src.user_requests.constants import MIN_MESSAGES_FOR_LEGAL_CONTACT
            message_count = chat.messages.count()
            if message_count < MIN_MESSAGES_FOR_LEGAL_CONTACT:
                raise serializers.ValidationError(
                    f"Chat must have at least {MIN_MESSAGES_FOR_LEGAL_CONTACT} messages"
                )
            return value
        except Chat.DoesNotExist:
            raise serializers.ValidationError("Chat not found or does not belong to user")


class LegalAssistanceRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.SerializerMethodField()
    chat_title = serializers.CharField(source='chat.title', read_only=True)
    chat_summary = serializers.CharField(source='chat.summary', read_only=True)
    
    class Meta:
        model = LegalAssistanceRequest
        fields = [
            'id',
            'user',
            'user_email',
            'user_phone',
            'chat',
            'chat_title',
            'chat_summary',
            'status',
            'created_at_ts',
            'in_progress_ts',
            'closed_at_ts',
        ]
        read_only_fields = ['id', 'created_at_ts', 'in_progress_ts', 'closed_at_ts']
    
    def get_user_phone(self, obj):
        """Get user phone number if available"""
        # Assuming phone might be stored in user profile or as a separate field
        # Adjust this based on your actual user model structure
        return getattr(obj.user, 'phone', None) or getattr(obj.user, 'phone_number', None)


class UpdateLegalAssistanceRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalAssistanceRequest
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transitions"""
        from src.user_requests.enums import LegalAssistanceRequestStatus
        valid_statuses = [status.value for status in LegalAssistanceRequestStatus]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
