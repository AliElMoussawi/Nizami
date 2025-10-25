from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone

from src.users.models import User
from src.plan.enums import InternalUtil, Tier
from src.plan.models import Plan
from src.subscription.models import UserSubscription
from src.common.utils import send_subscription_success_email


def _compute_expiry_date(plan: Plan) -> datetime:
    now = timezone.now()
    interval_count = plan.interval_count or 1

    if plan.interval_unit == InternalUtil.MONTH:
        return now + relativedelta(months=interval_count)
    if plan.interval_unit == InternalUtil.YEAR:
        return now + relativedelta(years=interval_count)

    raise ValueError('Unsupported plan interval unit')


@transaction.atomic
def create_subscription_for_user(user, plan: Plan) -> UserSubscription:
    expiry_date = _compute_expiry_date(plan)

    subscription = UserSubscription(
        user=user,
        plan=plan,
        is_active=True,
        expiry_date=expiry_date,
        credit_amount = plan.credit_amount,
        credit_type = plan.credit_type,
        is_unlimited= plan.is_unlimited
    )
    subscription.save()

    return subscription

@transaction.atomic
def upgrade_user_subscription_plan(user, plan: Plan) -> UserSubscription:
    # Get all active user subscriptions
    active_subscriptions = UserSubscription.objects.filter(user=user, is_active=True)
    
    if active_subscriptions.exists():
        now = timezone.now()
        active_subscriptions.update(
            is_active=False,
            deactivated_at=now
        )
    subscription = create_subscription_for_user(user=user, plan=plan)
    try:
        send_subscription_success_email(user, subscription, plan)
    except Exception as e:
        print(f"Failed to send subscription success email: {e}")
    return subscription

def create_basic_subscription_for_user(user) -> UserSubscription:
    if UserSubscription.objects.filter(user=user, plan__tier=Tier.BASIC).exists():
        raise ValueError("You are already enrolled in the basic plan")

    if UserSubscription.objects.filter(user=user).exists():
        return ValueError("You are not eligible for the free plan - past subscriptions exist")
        
    basic_plan = Plan.objects.filter(tier=Tier.BASIC).order_by("created_at").first()
    if basic_plan is None:
        raise ValueError("Basic plan is not configured")

    return create_subscription_for_user(user, basic_plan)

def upgrade_user_subscription_user_id_and_plan_id(user_id, plan_uuid):
    user = User.objects.get(id=user_id)
    plan = Plan.objects.get(uuid=plan_uuid)
    subscription = upgrade_user_subscription_plan(user=user, plan=plan)
    return subscription