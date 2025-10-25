from dateutil import relativedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db import transaction
import logging
import uuid
from src.subscription.services import upgrade_user_subscription_plan
from src.plan.enums import CreditType, Tier
from src.subscription.models import UserSubscription
from src.users.models import User
from src.ledger.enums import SubscriptionValidationCode
from src.payment.models import UserPaymentSource
from src.payment.services.moyasar_payment_service import get_moyasar_payment_service
from src.payment.enums import Currency, PaymentSourceType
from src.payment.enums import MoyasarPaymentStatus
from django.conf import settings

logger = logging.getLogger(__name__)

def pre_message_processing_validate(user: User):
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
        subscription = UserSubscription.objects.filter(
            user=user, 
            expiry_date__gte=timezone.now()
        ).latest('created_at')
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
        
    return True
        


@transaction.atomic
def decrement_credits_post_message(user: User):
    try:
        subscription = UserSubscription.objects.filter(
            user=user, 
            expiry_date__gte=timezone.now()
        ).latest('created_at')
        if user is None or subscription is None:
            raise ValidationError({
                'code': SubscriptionValidationCode.GENERAL_ERROR,
                'detail': 'Post message decrement - user or subscription is None',
            })
        
        #unlimited plan -> do nothing for credits
        if subscription.is_unlimited :
            return True
        
        if subscription.credit_type == CreditType.MESSAGES and subscription.credit_amount > 0:
            subscription.credit_amount -= 1
            subscription.save()
            
        return True
    except Exception as e:
        logger.error(f"User id: {user.id} - error: {e}")
        return False


@transaction.atomic
def renew_user_subscription():
    """
    Renew user subscriptions that are expiring soon.
    
    Requirements handled:
    - Get latest subscription per user (filter out deactivated ones)
    - Filter subscriptions assigned to active and non-deleted plans
    - Only include subscriptions created in the last month
    - Exclude BASIC tier subscriptions
    - Get subscriptions expiring in the next 6 hours
    - Validate users have valid payment tokens
    """
    now = timezone.now()
    expiration_threshold = now + relativedelta(hours=6)
    one_month_ago = now - relativedelta(months=1)
    
    logger.info(f"Starting subscription renewal process. Looking for subscriptions expiring before {expiration_threshold}")
    
    # Get latest active subscription per user that meets all criteria
    # This query ensures we get the most recent subscription per user
    latest_subscriptions = UserSubscription.objects.filter(
        is_active=True,
        deactivated_at__isnull=True,
        expiry_date__lte=expiration_threshold,
        created_at__gte=one_month_ago,  # Only subscriptions created in last month
        plan__tier__ne=Tier.BASIC,  # Exclude BASIC tier
        plan__is_active=True,  # Plan must be active
        plan__is_deleted=False,  # Plan must not be deleted
        user__is_active=True,  # User must be active
        user__payment_sources__is_active=True,  # User must have active payment sources
        user__payment_sources__is_default=True  # User must have default payment source
    ).select_related('user', 'plan').distinct('user')
    
    total_subscriptions = latest_subscriptions.count()
    if total_subscriptions == 0:
        logger.info("No subscriptions found for renewal")
        return {
            'renewed_count': 0,
            'failed_count': 0,
            'total_processed': 0,
            'message': 'No subscriptions found for renewal'
        }
    
    renewed_count = 0
    failed_count = 0
    skipped_count = 0
    
    for subscription in latest_subscriptions:
        try:
            logger.info(f"Processing subscription for user {subscription.user.id} (plan: {subscription.plan.name}, expires: {subscription.expiry_date})")
            if not _validate_subscription_for_renewal(subscription):
                skipped_count += 1
                logger.warning(f"✗ Skipped renewal for user {subscription.user.id} - validation failed")
                continue
                
            success = _attempt_subscription_renewal(subscription)
            if success:
                renewed_count += 1
                logger.info(f"✓ Successfully renewed subscription for user {subscription.user.id}")
            else:
                failed_count += 1
                logger.warning(f"✗ Failed to renew subscription for user {subscription.user.id}")
                
        except Exception as e:
            logger.error(f"✗ Exception during renewal for user {subscription.user.id}: {str(e)}", exc_info=True)
            failed_count += 1
    
    logger.info(f"Subscription renewal completed. Renewed: {renewed_count}, Failed: {failed_count}, Skipped: {skipped_count}, Total: {total_subscriptions}")
    return {
        'renewed_count': renewed_count,
        'failed_count': failed_count,
        'skipped_count': skipped_count,
        'total_processed': renewed_count + failed_count + skipped_count,
        'total_found': total_subscriptions
    }


def _validate_subscription_for_renewal(subscription: UserSubscription) -> bool:
    try:
        if not subscription.user.is_active:
            logger.warning(f"User {subscription.user.id} is inactive")
            return False
        
        if not subscription.plan.is_active or subscription.plan.is_deleted:
            logger.warning(f"Plan {subscription.plan.uuid} is inactive or deleted")
            return False
        
        if not subscription.is_active or subscription.deactivated_at is not None:
            logger.warning(f"Subscription {subscription.uuid} is inactive or deactivated")
            return False
        
        payment_source = UserPaymentSource.objects.filter(
            user=subscription.user,
            is_active=True,
            is_default=True
        ).first()
        
        if not payment_source:
            logger.warning(f"No active default payment source found for user {subscription.user.id}")
            return False
        
        # Check if payment token is valid (not empty)
        if not payment_source.token or payment_source.token.strip() == '':
            logger.warning(f"Invalid payment token for user {subscription.user.id}")
            return False
        
        # Check if subscription hasn't already been renewed recently (within last hour)
        if subscription.last_renewed and subscription.last_renewed > timezone.now() - relativedelta(hours=1):
            logger.warning(f"Subscription {subscription.uuid} was renewed recently")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating subscription {subscription.uuid}: {str(e)}", exc_info=True)
        return False


@transaction.atomic
def _attempt_subscription_renewal(subscription: UserSubscription) -> bool:
    try:
        logger.info(f"Attempting renewal for user {subscription.user.id}")
        
        # Double-check subscription is still valid (race condition protection)
        if not subscription.is_active or subscription.deactivated_at is not None:
            logger.warning(f"Subscription {subscription.uuid} became inactive during processing")
            return False

        # Get user's default payment source (already validated in _validate_subscription_for_renewal)
        payment_source = UserPaymentSource.objects.filter(
            user=subscription.user,
            is_active=True,
            is_default=True
        ).first()
        
        if not payment_source:
            logger.error(f"No active default payment source found for user {subscription.user.id}")
            return False
        
        logger.info(f"Found payment source for user {subscription.user.id}: {payment_source.token_type}")
        
        # Create payment
        payment_service = get_moyasar_payment_service()
        payment_id = f"renewal-{str(uuid.uuid4())}"
        
        logger.info(f"Creating payment {payment_id} for user {subscription.user.id} (amount: {subscription.plan.price_cents} SAR)")
        
        payment_result = payment_service.create_payment(
            payment_source_type=PaymentSourceType.TOKEN,
            given_id=payment_id,
            amount=subscription.plan.price_cents,
            currency=Currency.SAR.name,
            description=f"Subscription renewal for {subscription.plan.name}",
            callback_url=getattr(settings, 'FRONTEND_URL', 'https://app.nizami.ai/') + '/payment/callback',
            token=payment_source.token,
            user_email=subscription.user.email,
            user_id=str(subscription.user.id),
            plan_id=str(subscription.plan.uuid)
        )
        
        if not payment_result or not payment_result.get('id'):
            logger.error(f"Failed to create payment for user {subscription.user.id} - no payment ID returned")
            return False
        
        logger.info(f"Payment created successfully for user {subscription.user.id}: {payment_result['id']}")
        
        # Fetch and sync payment status
        synced_payment = payment_service.fetch_and_sync_payment(payment_result['id'])
        
        if synced_payment and synced_payment.status == MoyasarPaymentStatus.PAID:
            logger.info(f"Payment successful for user {subscription.user.id}, creating new subscription")
           # _create_renewed_subscription(subscription) --- This is already handled by payment_service.fetch_and_sync_payment(payment_result['id'])
            
            # Update last_renewed timestamp to prevent duplicate renewals
            subscription.last_renewed = timezone.now()
            subscription.save(update_fields=['last_renewed'])
            
            logger.info(f"Successfully renewed subscription for user {subscription.user.id}")
            return True
        else:
            payment_status = synced_payment.status if synced_payment else 'No payment result'
            logger.warning(f"Payment failed for user {subscription.user.id}: {payment_status}")
            
            # Log payment failure details for debugging
            if synced_payment:
                logger.warning(f"Payment details - ID: {synced_payment.id}, Status: {synced_payment.status}, Amount: {synced_payment.amount}")
            
            return False
            
    except Exception as e:
        logger.error(f"Error during renewal for user {subscription.user.id}: {str(e)}", exc_info=True)
        return False


def _create_renewed_subscription(subscription: UserSubscription):
    try:
        logger.info(f"Creating renewed subscription for user {subscription.user.id}")
        upgrade_user_subscription_plan(
            user=subscription.user, 
            plan=subscription.plan
        )
        logger.info(f"Successfully created renewed subscription for user {subscription.user.id}")
    except Exception as e:
        logger.error(f"Failed to create renewed subscription for user {subscription.user.id}: {str(e)}", exc_info=True)
        raise