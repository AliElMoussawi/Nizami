from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model

from src.subscription.models import UserSubscription
from src.plan.serializers import ListPlanSerializer
from src.users.serializers import UserSerializer

User = get_user_model()


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = ListPlanSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            'uuid',
            'user',
            'plan',
            'is_active',
            'credit_amount',
            'credit_type',
            'is_unlimited',
            'expiry_date',
            'last_renewed',
            'deactivated_at',
            'created_at',
            'updated_at',
         
        ]
        read_only_fields = fields


class CreateUserSubscriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = UserSubscription
        fields = [
            'user_email',
            'plan',
            'credit_amount',
            'credit_type',
            'is_unlimited',
            'expiry_date',
        ]

    def validate_user_email(self, value):
        try:
            user = User.objects.get(email=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address. Please check the email and try again.")

    def validate(self, data):
        user = data.get('user_email')  # This will be the User instance after validation
        
        # Check if user already has an active subscription
        existing_active = UserSubscription.objects.filter(
            user=user,
            is_active=True
        ).first()
        
        if existing_active:
            user_name = f"{user.first_name} {user.last_name}".strip() or user.email
            raise serializers.ValidationError({
                'user_email': f'User {user_name} already has an active subscription. Please deactivate the existing subscription first.'
            })
        
        # Validate expiry date is in the future
        if data.get('expiry_date') and data['expiry_date'] <= timezone.now():
            raise serializers.ValidationError({
                'expiry_date': 'Expiry date must be in the future.'
            })
        
        # Set default credit type to MESSAGES
        if not data.get('credit_type'):
            data['credit_type'] = 'MESSAGES'
        
        return data

    def create(self, validated_data):
        # Replace user_email with user in the data
        validated_data['user'] = validated_data.pop('user_email')
        validated_data['is_active'] = True  # New subscriptions are active by default
        return super().create(validated_data)


class UpdateUserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = [
            'is_active',
            'credit_amount',
            'credit_type',
            'is_unlimited',
            'expiry_date',
        ]

    def validate(self, data):
        # If activating, check if user already has an active subscription
        if data.get('is_active') is True:
            existing_active = UserSubscription.objects.filter(
                user=self.instance.user,
                is_active=True
            ).exclude(uuid=self.instance.uuid)
            
            if existing_active.exists():
                raise serializers.ValidationError({
                    'is_active': 'User already has an active subscription.'
                })
        
        # Validate expiry date is in the future
        if data.get('expiry_date') and data['expiry_date'] <= timezone.now():
            raise serializers.ValidationError({
                'expiry_date': 'Expiry date must be in the future.'
            })
        
        return data


