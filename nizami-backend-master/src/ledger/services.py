from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError


from src.plan.enums import InternalUtil, Tier, CreditType
from src.plan.models import Plan
from src.subscription.models import UserSubscription
from src.users.models import User
from src.ledger.enums import SubscriptionValidationCode





def pre_message_processing_validate(user:User):
    ''' We do not check if the plan of a user is deactivate by the admin - 
    meaning the plan is no longer available because this should - Because if a user subscribes today, 
    we cannot tomorrow tell him your plan is not available anymore.  However, he won't be able to renew and so on ''' 

    # Validate user state
    if user is None or not user.is_active:
        raise ValidationError({
            'code': SubscriptionValidationCode.USER_INACTIVE,
            'detail': 'User is inactive.',
        })

    try:
        subscription = UserSubscription.objects.get(user=user, is_active=True)
    except UserSubscription.DoesNotExist:
        raise ValidationError({
            'code': SubscriptionValidationCode.SUBSCRIPTION_NOT_FOUND,
            'detail': 'No active subscription found.',
        })
    except UserSubscription.MultipleObjectsReturned:
        raise ValidationError({
            'code': SubscriptionValidationCode.SUBSCRIPTION_MULTIPLE_ACTIVE,
            'detail': 'Multiple active subscriptions found.',
        })

    # 1- Check if subscription expired
    if subscription.expiry_date <= timezone.now():
        raise ValidationError({
            'code': SubscriptionValidationCode.SUBSCRIPTION_EXPIRED,
            'detail': 'Subscription has expired.',
        })

    # 2- Check if we still have credits for messages for limited plans - explicit checking credit_type because what if we added other types
    if not subscription.is_unlimited and subscription.credit_type == CreditType.MESSAGES and subscription.credit_amount <= 0:
        raise ValidationError({
            'code': SubscriptionValidationCode.NO_MESSAGE_CREDITS,
            'detail': 'No remaining message credits.',
        })
        
    return user, subscription
        



def decrement_credits_post_message(user:User, subscription:UserSubscription):
    if user is None or subscription is None:
        raise ValidationError({
            'code': SubscriptionValidationCode.GENERAL_ERROR,
            'detail': 'Post message decrement - user or subscription is None',
        })
    
    #unlimited plan -> do nothing for credits
    if subscription.is_unlimited :
        return
    
    if not subscription.is_unlimited and subscription.credit_type == CreditType.MESSAGES and subscription.credit_amount > 0:
        subscription.credit_amount -= 1
        subscription.save()
        return
        
    