from django_q.tasks import schedule
from django_q.models import Schedule
from django.core.management import call_command
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

if not Schedule.objects.filter(name="renew_user_subscription").exists():
    schedule(
        func='src.ledger.tasks.renew_user_subscription_task',
        name="renew_user_subscription",
        schedule_type='I',                          # interval schedule
        minutes=120,                                # every 2 hours (4 times per day)
        repeats=-1,                                 # run forever
        timeout=1800,                               # 30 minutes timeout
    )
    logger.info("Scheduled task 'renew_user_subscription' created successfully")
else:
    logger.info("Scheduled task 'renew_user_subscription' already exists")
