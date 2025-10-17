from django.db import models

class Tier(models.TextChoices):
    BASIC = 'BASIC', 'Basic'
    PLUS =  'PLUS', 'Plus'
    PREMIUM_MONTHLY = 'PREMIUM_MONTHLY', 'Premium-Monthly'
    PREMIUM_YEARLY = 'PREMIUM_YEARLY', 'Premium-Yearly'
    ADVANCED_PLUS = 'ADVANCED_PLUS', 'Advanced Plus'

class InternalUtil(models.TextChoices):
    MONTH = 'MONTH', 'Month'
    YEAR = 'YEAR', 'Year'
    
class CreditType(models.TextChoices):
    MESSAGES = 'MESSAGES', 'Messages'