from django.db import models
from .enums import CreditType, InternalUtil, Tier
import uuid


class Plan(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=50, choices=Tier.choices) 
    description = models.TextField(blank=True, null=True)
    price_cents = models.BigIntegerField()
    currency = models.CharField(max_length=10, default='USD')
    interval_unit = models.CharField(max_length=20, choices=InternalUtil.choices, blank=True, null=True) 
    interval_count = models.IntegerField(default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    credit_amount = models.IntegerField(blank=True, null=True)
    credit_type = models.CharField(max_length=50, choices=CreditType.choices)
    is_unlimited = models.BooleanField(default=False)
    rollover_allowed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plans'

    def __str__(self):
        return f"{self.name} ({self.tier or 'no tier'})"
