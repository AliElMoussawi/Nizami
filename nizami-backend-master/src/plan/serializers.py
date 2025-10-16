from rest_framework import serializers

from .models import Plan


class ListPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'uuid',
            'name',
            'tier',
            'description',
            'price_cents',
            'currency',
            'interval_unit',
            'interval_count',
            'is_active',
            'is_deleted',
            'credit_amount',
            'credit_type',
            'is_unlimited',
            'rollover_allowed',
        ]


class CreateUpdatePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'uuid',
            'name',
            'tier',
            'description',
            'price_cents',
            'currency',
            'interval_unit',
            'interval_count',
            'is_active',
            'is_deleted',
            'credit_amount',
            'credit_type',
            'is_unlimited',
            'rollover_allowed',
        ]
        read_only_fields = ['uuid']
