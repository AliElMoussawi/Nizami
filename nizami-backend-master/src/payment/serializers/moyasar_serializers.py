import logging
from rest_framework import serializers

from ..enums import MoyasarWebhookEventType, Currency, PaymentSourceType
from ..models import UserPaymentSource, MoyasarPayment, MoyasarInvoice

logger = logging.getLogger(__name__)


class MoyasarPaymentSourceSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    company = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    number = serializers.CharField(required=False, allow_null=True)
    gateway_id = serializers.CharField(required=False, allow_null=True)
    reference_number = serializers.CharField(required=False, allow_null=True)
    token = serializers.CharField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_null=True)
    transaction_url = serializers.URLField(required=False, allow_null=True)
    response_code = serializers.CharField(required=False, allow_null=True)
    authorization_code = serializers.CharField(required=False, allow_null=True)
    issuer_name = serializers.CharField(required=False, allow_null=True)
    issuer_country = serializers.CharField(required=False, allow_null=True)
    issuer_card_type = serializers.CharField(required=False, allow_null=True)
    issuer_card_category = serializers.CharField(required=False, allow_null=True)

class MoyasarPaymentSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    status = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)
    fee = serializers.IntegerField(required=False, default=0)
    currency = serializers.ChoiceField(choices=Currency.choices, required=True)
    refunded = serializers.IntegerField(required=False, default=0)
    refunded_at = serializers.DateTimeField(required=False, allow_null=True)
    captured = serializers.IntegerField(required=False, default=0)
    captured_at = serializers.DateTimeField(required=False, allow_null=True)
    voided_at = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount_format = serializers.CharField(required=False, allow_null=True)
    fee_format = serializers.CharField(required=False, allow_null=True)
    refunded_format = serializers.CharField(required=False, allow_null=True)
    captured_format = serializers.CharField(required=False, allow_null=True)
    ip = serializers.IPAddressField(required=False, allow_null=True)
    callback_url = serializers.URLField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False, allow_null=True, default=dict)
    
    # Nested fields
    source = MoyasarPaymentSourceSerializer(required=False, allow_null=True)
    invoice_id = serializers.CharField(required=False, allow_null=True)


class MoyasarInvoiceSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    status = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)
    currency = serializers.ChoiceField(choices=Currency.choices, required=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    logo_url = serializers.URLField(required=False, allow_null=True)
    amount_format = serializers.CharField(required=False, allow_null=True)
    url = serializers.URLField(required=False, allow_null=True)
    callback_url = serializers.URLField(required=False, allow_null=True)
    expired_at = serializers.DateTimeField(required=False, allow_null=True)
    back_url = serializers.URLField(required=False, allow_null=True)
    success_url = serializers.URLField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, allow_null=True)
    updated_at = serializers.DateTimeField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False, allow_null=True, default=dict)
    
    # Nested payments (optional)
    payments = serializers.ListField(
        child=MoyasarPaymentSerializer(),
        required=False,
        allow_null=True,
        default=list
    )


class MoyasarWebhookSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    type = serializers.ChoiceField(choices=MoyasarWebhookEventType.choices, required=True)
    created_at = serializers.DateTimeField(required=True)
    secret_token = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    account_name = serializers.CharField(required=False, allow_null=True)
    live = serializers.BooleanField(required=True)
    
    data = MoyasarPaymentSerializer(required=True)


class CreateInvoiceRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True, min_value=1)
    currency = serializers.ChoiceField(choices=Currency.choices, default=Currency.SAR)
    description = serializers.CharField(required=True, max_length=255)
    callback_url = serializers.URLField(required=True)
    success_url = serializers.URLField(required=False, allow_null=True)
    back_url = serializers.URLField(required=False, allow_null=True)
    expired_at = serializers.DateTimeField(required=False, allow_null=True)


class CreatePaymentRequestSerializer(serializers.Serializer):
    payment_source_type = serializers.ChoiceField(choices=PaymentSourceType.choices, required=True)
    amount = serializers.IntegerField(required=True, min_value=1)
    currency = serializers.ChoiceField(choices=Currency.choices, default=Currency.SAR)
    description = serializers.CharField(required=True, max_length=255)
    callback_url = serializers.URLField(required=True)
    
    card_name = serializers.CharField(required=False, allow_null=True)
    card_number = serializers.CharField(required=False, allow_null=True)
    card_month = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=12)
    card_year = serializers.IntegerField(required=False, allow_null=True, min_value=2024)
    card_cvc = serializers.CharField(required=False, allow_null=True)
    
    token = serializers.CharField(required=False, allow_null=True)
    save_card = serializers.BooleanField(default=False)
    
    def validate(self, data):
        payment_source_type = data.get('payment_source_type')
        
        if payment_source_type == PaymentSourceType.CREDIT_CARD:
            required_fields = ['card_name', 'card_number', 'card_month', 'card_year', 'card_cvc']
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError({
                    'card_details': f'Card payment requires: {", ".join(missing)}'
                })
        
        elif payment_source_type == PaymentSourceType.TOKEN:
            if not data.get('token'):
                raise serializers.ValidationError({
                    'token': 'Token is required for token payment type'
                })
        
        return data


class UserPaymentSourceSerializer(serializers.ModelSerializer):
    last_four = serializers.SerializerMethodField()
    card_type = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPaymentSource
        fields = [
            'uuid', 'token', 'token_type', 'is_default', 
            'is_active', 'nickname', 'last_four', 'card_type', 'created_at'
        ]
        read_only_fields = ['uuid', 'token', 'token_type', 'created_at']
    
    def get_last_four(self, obj):
        if obj.payment_source and obj.payment_source.number:
            return obj.payment_source.number[-4:]
        return None
    
    def get_card_type(self, obj):
        if obj.payment_source:
            return obj.payment_source.company or obj.payment_source.type
        return None


class AddPaymentSourceRequestSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    nickname = serializers.CharField(required=False, allow_blank=True, max_length=50)
    set_as_default = serializers.BooleanField(default=False)


class PaymentDetailSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    
    class Meta:
        model = MoyasarPayment
        fields = [
            'id', 'internal_uuid', 'status', 'amount', 'fee', 'currency', 
            'refunded', 'refunded_at', 'captured', 'captured_at',
            'voided_at', 'description', 'amount_format', 'fee_format',
            'created_at', 'updated_at', 'metadata', 'source'
        ]
    
    def get_source(self, obj):
        if obj.source:
            return {
                'type': obj.source.type,
                'company': obj.source.company,
                'last_four': obj.source.number[-4:] if obj.source.number else None,
            }
        return None


class InvoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoyasarInvoice
        fields = [
            'id', 'status', 'amount', 'currency', 'description',
            'url', 'callback_url', 'expired_at', 'back_url', 
            'success_url', 'created_at', 'updated_at', 'metadata'
        ]