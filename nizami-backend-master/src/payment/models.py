from enum import unique
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
import uuid
from .enums import MoyasarPaymentStatus, MoyasarWebhookEventType, PaymentSourceType, Currency

class MoyasarInvoice(models.Model):
    internal_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    id = models.UUIDField(unique=True, null=True, blank=True)
    status = models.CharField(max_length=50)
    amount = models.PositiveIntegerField()
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.SAR)
    description = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    amount_format = models.CharField(max_length=50, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    callback_url = models.URLField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    back_url = models.URLField(null=True, blank=True)
    success_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    metadata = models.JSONField(default=dict, blank=True)
    def __str__(self):
        return f"Invoice {self.id} - {self.status.upper()} - {self.amount} {self.currency}"


class MoyasarPaymentSource(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    type = models.CharField(max_length=50, choices=PaymentSourceType.choices) # e.g. creditcard, token
    company = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=120, null=True, blank=True)
    number = models.CharField(max_length=30, null=True, blank=True)
    gateway_id = models.CharField(max_length=120, null=True, blank=True)
    reference_number = models.CharField(max_length=120, null=True, blank=True)
    token = models.CharField(max_length=120, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    transaction_url = models.URLField(null=True, blank=True)
    response_code = models.CharField(max_length=50, null=True, blank=True)
    authorization_code = models.CharField(max_length=50, null=True, blank=True)
    issuer_name = models.CharField(max_length=120, null=True, blank=True)
    issuer_country = models.CharField(max_length=50, null=True, blank=True)
    issuer_card_type = models.CharField(max_length=50, null=True, blank=True)
    issuer_card_category = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.type} ({self.company or 'unknown'})"


class UserPaymentSource(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_sources'
    )
    payment_source = models.ForeignKey(
        MoyasarPaymentSource,
        on_delete=models.CASCADE,
        related_name='user_links'
    )
    token = models.CharField(max_length=120, help_text="Payment token for reuse")
    token_type = models.CharField(
        max_length=50, 
        choices=PaymentSourceType.choices,
        default=PaymentSourceType.TOKEN,
        help_text="Type of the payment token"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the user's default payment method"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this payment source is active"
    )
    nickname = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="User-friendly name for this payment method"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        unique_together = [['user', 'token']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'is_default']),
        ]

    def __str__(self):
        default_text = " (Default)" if self.is_default else ""
        nickname_text = f" - {self.nickname}" if self.nickname else ""
        return f"{self.user.email} - {self.token_type}{nickname_text}{default_text}"

    def save(self, *args, **kwargs):
        if self.is_default:
            with transaction.atomic():
                UserPaymentSource.objects.select_for_update().filter(
                    user=self.user,
                    is_default=True
                ).exclude(uuid=self.uuid).update(is_default=False)
        super().save(*args, **kwargs)


class MoyasarPayment(models.Model):

    internal_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    id = models.UUIDField(unique=True, null=True, blank=True)
    status = models.CharField(max_length=50, choices=MoyasarPaymentStatus.choices)
    amount = models.PositiveIntegerField()
    fee = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.SAR)
    refunded = models.PositiveIntegerField(default=0)
    refunded_at = models.DateTimeField(null=True, blank=True)
    captured = models.PositiveIntegerField(default=0)
    captured_at = models.DateTimeField(null=True, blank=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    amount_format = models.CharField(max_length=50, null=True, blank=True)
    fee_format = models.CharField(max_length=50, null=True, blank=True)
    refunded_format = models.CharField(max_length=50, null=True, blank=True)
    captured_format = models.CharField(max_length=50, null=True, blank=True)

    ip = models.GenericIPAddressField(null=True, blank=True)
    callback_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # JSON field for extra metadata
    metadata = models.JSONField(default=dict, blank=True)
    invoice = models.ForeignKey(
        MoyasarInvoice,
        related_name="payments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    # Relation to PaymentSource
    source = models.OneToOneField(MoyasarPaymentSource, on_delete=models.CASCADE, null=True, blank=True, related_name="payment")
    def __str__(self):
        return f"{self.id} - {self.status.upper()} - {self.amount} {self.currency}"

class MoyasarWebhookEvent(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=20, choices=MoyasarWebhookEventType.choices)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    live = models.BooleanField(default=False)
    event_created_at = models.DateTimeField()
    data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        default_permissions = ('add', 'change', 'delete', 'view')
