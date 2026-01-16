from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

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
    
    def validate(self, attrs):
        """Validate user subscription and request limit"""
        user = self.context['request'].user
        from src.user_requests.constants import MAX_REQUESTS_FOR_FREE_EXPIRED_USERS
        from src.subscription.models import UserSubscription
        from src.plan.enums import Tier
        
        # Check if user has free subscription (BASIC tier) or expired subscription
        is_free_or_expired = False
        
        try:
            # Get the latest subscription (even if expired)
            subscription = UserSubscription.objects.filter(
                user=user
            ).latest('created_at')
            
            # Check if it's BASIC tier (free)
            if subscription.plan.tier == Tier.BASIC:
                is_free_or_expired = True
            # Check if subscription is expired
            elif subscription.expiry_date < timezone.now():
                is_free_or_expired = True
        except UserSubscription.DoesNotExist:
            # No subscription found, treat as free/expired
            is_free_or_expired = True
        
        # If user is on free or expired subscription, check request limit
        if is_free_or_expired:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_requests_count = LegalAssistanceRequest.objects.filter(
                user=user,
                created_at_ts__gte=thirty_days_ago
            ).count()
            
            if recent_requests_count >= MAX_REQUESTS_FOR_FREE_EXPIRED_USERS:
                raise serializers.ValidationError(
                    f"You have reached the maximum limit of {MAX_REQUESTS_FOR_FREE_EXPIRED_USERS} legal assistance requests in the last 30 days. Please upgrade your subscription to continue."
                )
        
        return attrs


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
            'in_charge',
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
        fields = ['status', 'in_charge']
    
    def validate_status(self, value):
        """Validate status transitions"""
        from src.user_requests.enums import LegalAssistanceRequestStatus
        valid_statuses = [status.value for status in LegalAssistanceRequestStatus]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate(self, attrs):
        """Validate that in_charge is provided when transitioning status"""
        instance = self.instance
        new_status = attrs.get('status')
        in_charge = attrs.get('in_charge')
        
        if instance and new_status:
            from src.user_requests.enums import LegalAssistanceRequestStatus
            original_status = instance.status
            
            # Check if status is changing
            if original_status != new_status:
                # Transitioning from NEW to IN_PROGRESS
                if original_status == LegalAssistanceRequestStatus.NEW.value and new_status == LegalAssistanceRequestStatus.IN_PROGRESS.value:
                    if not in_charge or not in_charge.strip():
                        raise serializers.ValidationError({
                            'in_charge': ['In Charge field is required when moving from New to In Progress status.']
                        })
                
                # Transitioning from IN_PROGRESS to CLOSED
                elif original_status == LegalAssistanceRequestStatus.IN_PROGRESS.value and new_status == LegalAssistanceRequestStatus.CLOSED.value:
                    if not in_charge or not in_charge.strip():
                        raise serializers.ValidationError({
                            'in_charge': ['In Charge field is required when moving from In Progress to Closed status.']
                        })
                
                # Transitioning directly from NEW to CLOSED
                elif original_status == LegalAssistanceRequestStatus.NEW.value and new_status == LegalAssistanceRequestStatus.CLOSED.value:
                    if not in_charge or not in_charge.strip():
                        raise serializers.ValidationError({
                            'in_charge': ['In Charge field is required when moving to Closed status.']
                        })
        
        return attrs