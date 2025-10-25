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
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'user_email': user.email,
            'password': password,
            'current_year': timezone.now().year,
        }
    )

    send_email(
        subject=subject,
        message=None,
        from_email=settings.EMAIL_FROM_ADDRESS,
        to=[user.email],
        fail_silently=False,
        html_message=message
    )



def send_welcome_mail(user):
    subject = 'Welcome to JP Ai'

    message = render_to_string(
        'welcome.html',
        context={
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'user_email': user.email,
            'current_year': timezone.now().year,
        }
    )

    send_email(
        subject=subject,
        message=None,
        from_email=settings.EMAIL_FROM_ADDRESS,
        to=[user.email],
        fail_silently=False,
        html_message=message
    )



def load_aspose_license():
    """
    Stub function for Aspose license loading.
    Aspose-words package is not available in this configuration.
    """
    pass


def get_email_template(template_name, user_language='ar'):
    if user_language == 'ar':
        return f'{template_name}_ar.html'
    return f'{template_name}_en.html'


def send_subscription_success_email(user, subscription, plan):
    template_name = get_email_template('subscription_success', user.language)
    subject = 'Subscription Successful - Nizami' if user.language == 'en' else 'اشتراك ناجح - نظامي'

    message = render_to_string(
        template_name,
        context={
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'user_email': user.email,
            'subscription_expiry_date': subscription.expiry_date,
            'plan_name': plan.name,
            'plan_price_cents': plan.price_cents,
            'plan_interval_unit': plan.interval_unit,
            'current_year': timezone.now().year,
        }
    )

    send_email(
        subject=subject,
        message=None,
        from_email=settings.EMAIL_FROM_ADDRESS,
        to=[user.email],
        fail_silently=False,
        html_message=message
    )



def send_subscription_cancelled_email(user, subscription, plan):
    template_name = get_email_template('subscription_cancelled', user.language)
    subject = 'Subscription Cancelled - Nizami' if user.language == 'en' else 'تم إلغاء الاشتراك - نظامي'

    message = render_to_string(
        template_name,
        context={
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'user_email': user.email,
            'subscription_expiry_date': subscription.expiry_date,
            'subscription_deactivated_at': subscription.deactivated_at,
            'plan_name': plan.name,
            'current_year': timezone.now().year,
        }
    )

    send_email(
        subject=subject,
        message=None,
        from_email=settings.EMAIL_FROM_ADDRESS,
        to=[user.email],
        fail_silently=False,
        html_message=message
    )



def send_payment_success_email(user, payment):
    template_name = get_email_template('payment_success', user.language)
    subject = 'Payment Successful - Nizami' if user.language == 'en' else 'دفع ناجح - نظامي'

    message = render_to_string(
        template_name,
        context={
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'user_email': user.email,
            'payment_amount': payment.amount,
            'payment_status': payment.status,
            'payment_method': payment.source.type if payment.source else None,
            'transaction_id': payment.id,
            'payment_created_at': payment.created_at,
            'current_year': timezone.now().year,
        }
    )

    send_email(
        subject=subject,
        message=None,
        from_email=settings.EMAIL_FROM_ADDRESS,
        to=[user.email],
        fail_silently=False,
        html_message=message
    )


def send_payment_failure_email(user, payment):
    template_name = get_email_template('payment_failure', user.language)
    subject = 'Payment Failed - Nizami' if user.language == 'en' else 'فشل الدفع - نظامي'

    message = render_to_string(
        template_name,
        context={
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'user_email': user.email,
            'payment_amount': payment.amount,
            'payment_status': payment.status,
            'payment_method': payment.source.type if payment.source else None,
            'transaction_id': payment.id,
            'payment_created_at': payment.created_at,
            'current_year': timezone.now().year,
        }
    )

    send_email(
        subject=subject,
        message=None,
        from_email=settings.EMAIL_FROM_ADDRESS,
        to=[user.email],
        fail_silently=False,
        html_message=message
    )


def chunk_array(arr, chunk_size):
    return [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]



def send_email(subject, html_message, from_email, to, message=None, fail_silently=False):
    send_mail(
        subject,
        message,
        from_email,
        to,
        fail_silently=fail_silently,
        html_message=html_message
    )