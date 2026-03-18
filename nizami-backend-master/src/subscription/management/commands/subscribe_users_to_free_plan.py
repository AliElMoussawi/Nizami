from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from src.users.models import User
from src.plan.models import Plan
from src.subscription.models import UserSubscription


class Command(BaseCommand):
    help = 'Subscribe all existing users without an active subscription to the free plan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually creating subscriptions',
        )
        parser.add_argument(
            '--plan-name',
            type=str,
            default='Free',
            help='Name of the free plan (default: "Free")',
        )
        parser.add_argument(
            '--duration-months',
            type=int,
            default=1,
            help='Duration of the subscription in months (default: 1)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        plan_name = options['plan_name']
        duration_months = options['duration_months']

        try:
            # Find the free plan
            try:
                free_plan = Plan.objects.get(name__iexact=plan_name, is_active=True, is_deleted=False)
                self.stdout.write(
                    self.style.SUCCESS(f'Found plan: {free_plan.name} (UUID: {free_plan.uuid})')
                )
            except Plan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Plan "{plan_name}" not found. Available plans:')
                )
                for plan in Plan.objects.filter(is_active=True, is_deleted=False):
                    self.stdout.write(f'  - {plan.name} ({plan.tier})')
                return
            except Plan.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.ERROR(f'Multiple plans found with name "{plan_name}". Please be more specific.')
                )
                return

            # Get all users without an active subscription
            users_without_subscription = User.objects.exclude(
                subscriptions__is_active=True
            ).distinct()

            total_users = users_without_subscription.count()

            if total_users == 0:
                self.stdout.write(
                    self.style.SUCCESS('All users already have an active subscription!')
                )
                return

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'DRY RUN MODE - Would subscribe {total_users} users to "{free_plan.name}" plan')
                )
                self.stdout.write('\nUsers to be subscribed:')
                for user in users_without_subscription[:10]:  # Show first 10
                    self.stdout.write(f'  - {user.username} ({user.email})')
                if total_users > 10:
                    self.stdout.write(f'  ... and {total_users - 10} more')
                return

            # Calculate expiry date
            expiry_date = timezone.now() + timedelta(days=30 * duration_months)

            # Create subscriptions
            subscriptions_created = 0
            errors = []

            for user in users_without_subscription:
                try:
                    UserSubscription.objects.create(
                        user=user,
                        plan=free_plan,
                        is_active=True,
                        credit_amount=free_plan.credit_amount,
                        credit_type=free_plan.credit_type,
                        is_unlimited=free_plan.is_unlimited,
                        expiry_date=expiry_date,
                    )
                    subscriptions_created += 1
                    self.stdout.write(f'✓ Subscribed: {user.username} ({user.email})')
                except Exception as e:
                    error_msg = f'✗ Failed to subscribe {user.username}: {str(e)}'
                    errors.append(error_msg)
                    self.stdout.write(self.style.ERROR(error_msg))

            # Summary
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully subscribed {subscriptions_created} users to "{free_plan.name}" plan'
                )
            )
            if errors:
                self.stdout.write(
                    self.style.WARNING(f'{len(errors)} errors occurred')
                )
            self.stdout.write(f'Expiry date: {expiry_date.strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write('=' * 50)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during subscription process: {e}')
            )
            raise

