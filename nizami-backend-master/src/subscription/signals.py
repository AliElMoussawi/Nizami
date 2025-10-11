from django.db.models.signals import post_save
from django.dispatch import receiver
from src.plan.enums import Tier
from src.users.models import User
from src.subscription.services import create_basic_subscription_for_user


@receiver(post_save, sender=User)
def create_basic_subscription(sender, instance: User, created: bool, **kwargs):
    if not created:
        return
    create_basic_subscription_for_user(instance, Tier.BASIC)


