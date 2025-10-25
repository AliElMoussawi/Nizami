from django_q.tasks import schedule
import logging

logger = logging.getLogger(__name__)

schedule(
    'django.core.management.call_command',  # Django helper for running management commands
    'renew_user_subscription',              # correct command name
    schedule_type='I',                      # interval schedule
    minutes=120,                            # every 2 hours (4 times per day)
    repeats=-1,                             # run forever
    timeout=1800,                           # 30 minutes timeout
)
