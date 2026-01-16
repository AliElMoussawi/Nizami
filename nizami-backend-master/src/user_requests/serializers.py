from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from src.chats.models import Chat
from src.plan.enums import Tier
from src.subscription.models import UserSubscription
from src.user_requests.constants import MAX_REQUESTS_FOR_FREE_EXPIRED_USERS, MIN_MESSAGES_FOR_LEGAL_CONTACT
from src.user_requests.enums import LegalAssistanceRequestStatus
from src.user_requests.models import LegalAssistanceRequest


class CreateLegalAssistanceRequestSerializer(serializers.Serializer):
    chat_id = serializers.IntegerField(required=True)
    
    def validate_chat_id(self, value):
        user = self.context['request'].user
        try:
            chat = Chat.objects.get(id=value, user=user)
            message_count = chat.messages.count()
            if message_count < MIN_MESSAGES_FOR_LEGAL_CONTACT:
                raise serializers.ValidationError(
                    f"Chat must have at least {MIN_MESSAGES_FOR_LEGAL_CONTACT} messages"
                )
            return value
        except Chat.DoesNotExist:
            raise serializers.ValidationError("Chat not found or does not belong to user")
    
    def validate(self, attrs):
        user = self.context['request'].user
        is_free_or_expired = False
        
        try:
            subscription = UserSubscription.objects.filter(
                user=user
            ).latest('created_at')
            
            if subscription.plan.tier == Tier.BASIC:
                is_free_or_expired = True
            elif subscription.expiry_date < timezone.now():
                is_free_or_expired = True
        except UserSubscription.DoesNotExist:
            is_free_or_expired = True
        
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
        return getattr(obj.user, 'phone', None) or getattr(obj.user, 'phone_number', None)


class UpdateLegalAssistanceRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalAssistanceRequest
        fields = ['status', 'in_charge']
    
    def validate_status(self, value):
        valid_statuses = [status.value for status in LegalAssistanceRequestStatus]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate(self, attrs):
        instance = self.instance
        new_status = attrs.get('status')
        in_charge = attrs.get('in_charge')
        
        if instance and new_status:
            original_status = instance.status
            
            if original_status != new_status:
                if original_status == LegalAssistanceRequestStatus.NEW.value and new_status == LegalAssistanceRequestStatus.IN_PROGRESS.value:
                    if not in_charge or not in_charge.strip():
                        raise serializers.ValidationError({
                            'in_charge': ['In Charge field is required when moving from New to In Progress status.']
                        })
                
                elif original_status == LegalAssistanceRequestStatus.IN_PROGRESS.value and new_status == LegalAssistanceRequestStatus.CLOSED.value:
                    if not in_charge or not in_charge.strip():
                        raise serializers.ValidationError({
                            'in_charge': ['In Charge field is required when moving from In Progress to Closed status.']
                        })
                
                elif original_status == LegalAssistanceRequestStatus.NEW.value and new_status == LegalAssistanceRequestStatus.CLOSED.value:
                    if not in_charge or not in_charge.strip():
                        raise serializers.ValidationError({
                            'in_charge': ['In Charge field is required when moving to Closed status.']
                        })
        
        return attrs