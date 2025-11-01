from django_q.tasks import schedule
from django_q.models import Schedule
from django.core.management import call_command
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def renew_user_subscription_task():
    try:
        logger.info("Starting subscription renewal task...")
        call_command('renew_user_subscription')
        logger.info("Subscription renewal task completed successfully")
        return "Success"
    except Exception as e:
        logger.error(f"Subscription renewal task failed: {str(e)}")
        raise


def setup_renewal_schedule():
    try:
        with transaction.atomic():
            # Use get_or_create to ensure only one schedule exists
            existing_schedule, created = Schedule.objects.get_or_create(
                name="renew_user_subscription",
                defaults={
                    'func': 'src.ledger.tasks.renew_user_subscription_task',
                    'schedule_type': 'I',  # interval schedule
                    'minutes': 120,  # every 2 hours
                    'repeats': -1,  # run forever
                }
            )
            
            if created:
                logger.info("Scheduled task 'renew_user_subscription' created successfully")
    except Exception as e:
        logger.error(f"Error setting up renewal schedule: {str(e)}", exc_info=True)
    
setup_renewal_schedule()

