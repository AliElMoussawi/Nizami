from django.db import models

import uuid

from django.db import models
from django.db.models import Q, UniqueConstraint
from django.core.exceptions import ValidationError

from src.users.models import User
from src.plan.models import Plan
from src.plan.enums import CreditType


class UserSubscription(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    credit_amount = models.IntegerField(blank=True, null=True)
    credit_type = models.CharField(max_length=50, choices=CreditType.choices, default=CreditType.MESSAGES)
    is_unlimited = models.BooleanField(default=False)
    expiry_date = models.DateTimeField(null=False, blank=False)
    last_renewed = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

    def clean(self):
        if self.is_active and self.user_id:
            qs = UserSubscription.objects.filter(user=self.user, is_active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({
                    'is_active': 'User already has an active subscription.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user'],
                condition=Q(is_active=True),
                name='unique_active_subscription_per_user',
            )
        ]