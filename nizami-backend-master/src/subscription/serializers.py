from rest_framework import serializers

from src.subscription.models import UserSubscription
from src.plan.serializers import ListPlanSerializer


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = ListPlanSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = [
            'uuid',
            'user',
            'plan',
            'is_active',
            'expiry_date',
            'last_renewed',
            'deactivated_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


