from django.db import models

class Tier(models.TextChoices):
    BASIC = 'BASIC', 'Basic'
    PLUS =  'PLUS', 'Plus'
    PREMIUM = 'PREMIUM', 'Premium'

class InternalUtil(models.TextChoices):
    MONTH = 'MONTH', 'Month'
    YEAR = 'YEAR', 'Year'
    
class CreditType(models.TextChoices):
    MESSAGES = 'MESSAGES', 'Messages'