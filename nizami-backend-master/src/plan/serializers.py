from rest_framework import serializers
from .models import Plan


class ListPlanSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    
    class Meta:
        model = Plan
        fields = [
            'uuid',
            'name',
            'tier',
            'description',
            'price_cents',
            'price',
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
    
    def get_price(self, obj):
        return obj.price_cents / 100.0  # Convert cents to dollars


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
        read_only_fields = ['uuid', 'is_active', 'is_deleted']

    def validate(self, data):
        # Check for duplicate active plans with same tier
        tier = data.get('tier')
        if tier:
            existing_plan = Plan.objects.filter(
                tier=tier,
                is_deleted=False
            ).exclude(
                uuid=self.instance.uuid if self.instance else None
            ).first()
            
            if existing_plan:
                raise serializers.ValidationError({
                    'tier': f'Another active plan with tier "{tier}" already exists. Please choose a different tier or deactivate the existing plan first.'
                })
        
        return data
