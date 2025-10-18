import os

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from src import settings


def get_db_url():
    db_config = settings.DATABASES['default']
    user = db_config.get('USER', 'messaging')
    password = db_config.get('PASSWORD', 'messaging')
    host = db_config.get('HOST', 'localhost')
    port = db_config.get('PORT', '54325')
    name = db_config.get('NAME', 'postgres')

    # Construct the database URL
    if user and password:
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return f"postgresql://{host}:{port}/{name}"


def send_welcome_with_password_message(user, password):
    subject = 'Welcome to JP Ai'

    message = render_to_string(
        'welcome_with_password.html',
        context={
            'app_url': settings.FRONTEND_DOMAIN,
            'user': user,
            'password': password,
            'current_year': timezone.now().year,
        }
    )

    send_mail(
        subject,
        None,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
        fail_silently=False,
        html_message=message
    )


def send_welcome_mail(user):
    subject = 'Welcome to JP Ai'

    message = render_to_string(
        'welcome.html',
        context={
            'user': user,
            'current_year': timezone.now().year,
        }
    )

    send_mail(
        subject,
        None,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
        fail_silently=False,
        html_message=message
    )


def load_aspose_license():
    """
    Stub function for Aspose license loading.
    Aspose-words package is not available in this configuration.
    """
    pass


def send_subscription_success_email(user, subscription, plan):
    subject = 'Subscription Successful - JP Ai'

    message = render_to_string(
        'subscription_success.html',
        context={
            'user': user,
            'subscription': subscription,
            'plan': plan,
            'current_year': timezone.now().year,
        }
    )

    send_mail(
        subject,
        None,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
        fail_silently=False,
        html_message=message
    )


def send_subscription_cancelled_email(user, subscription, plan):
    subject = 'Subscription Cancelled - JP Ai'

    message = render_to_string(
        'subscription_cancelled.html',
        context={
            'user': user,
            'subscription': subscription,
            'plan': plan,
            'current_year': timezone.now().year,
        }
    )

    send_mail(
        subject,
        None,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
        fail_silently=False,
        html_message=message
    )


def send_payment_success_email(user, payment):
    subject = 'Payment Successful - JP Ai'

    message = render_to_string(
        'payment_success.html',
        context={
            'user': user,
            'payment': payment,
            'current_year': timezone.now().year,
        }
    )

    send_mail(
        subject,
        None,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
        fail_silently=False,
        html_message=message
    )


def send_payment_failure_email(user, payment):
    subject = 'Payment Failed - JP Ai'

    message = render_to_string(
        'payment_failure.html',
        context={
            'user': user,
            'payment': payment,
            'current_year': timezone.now().year,
        }
    )

    send_mail(
        subject,
        None,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
        fail_silently=False,
        html_message=message
    )


def chunk_array(arr, chunk_size):
    return [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]
