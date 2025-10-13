import enum

from django.db import models

class MoyasarPaymentStatus(models.TextChoices):
    INITIATED = 'initiated', 'Initiated'
    PAID = 'paid', 'Paid'
    FAILED = 'failed', 'Failed'
    AUTHORIZED = 'authorized', 'Authorized'
    CAPTURED = 'captured', 'Captured'
    REFUNDED = 'refunded', 'Refunded'
    VOIDED = 'voided', 'Voided'
    VERIFIED = 'verified', 'Verified'

    @classmethod
    def is_final_status(cls, status):
        return status not in [cls.INITIATED, cls.AUTHORIZED]

class PaymentSourceType(models.TextChoices):
    TOKEN = 'token', 'Token'
    CREDIT_CARD = 'creditcard', 'Credit Card'


class Currency(models.TextChoices):
    SAR = 'SAR', 'Saudi Riyal'
    USD = 'USD', 'US Dollar'


class MoyasarWebhookEventType(models.TextChoices):
    PAYMENT_PAID = 'payment_paid', 'Payment Paid'
    PAYMENT_FAILED = 'payment_failed', 'Payment Failed'
    PAYMENT_AUTHORIZED = 'payment_authorized', 'Payment Authorized'
    PAYMENT_CAPTURED = 'payment_captured', 'Payment Captured'
    PAYMENT_REFUNDED = 'payment_refunded', 'Payment Refunded'
    PAYMENT_VOIDED = 'payment_voided', 'Payment Voided'

