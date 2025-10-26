from django.db import models

class SubscriptionCreator(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    SYSTEM =  'SYSTEM', 'System'
    USER = 'USER', 'User'