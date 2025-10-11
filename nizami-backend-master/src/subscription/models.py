from django.db import models

import os
import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from src.users.models import User
from src.plan.models import Plan


class UserSubscription(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=False, blank=False)
    last_renewed = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)