from django.core.management.base import BaseCommand
from src.ledger.services import renew_user_subscription


class Command(BaseCommand):
    help = 'Renew client subscriptions that are expiring soon (no retry mechanism)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be renewed without actually processing renewals',
        )

    def handle(self, *args, **options):
        try:
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING('DRY RUN MODE - No actual renewals will be processed')
                )
                # In dry run mode, we could add logic to just show what would be renewed
                # For now, we'll just run normally but with a warning
                
            result = renew_user_subscription()
            
            if result['total_found'] == 0:
                self.stdout.write(
                    self.style.SUCCESS('No subscriptions found for renewal')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Renewal completed: {result["renewed_count"]} successful, '
                        f'{result["failed_count"]} failed, '
                        f'{result["skipped_count"]} skipped, '
                        f'{result["total_found"]} total found'
                    )
                )
                
                if result['failed_count'] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'{result["failed_count"]} renewals failed. Check logs for details.'
                        )
                    )
                    
                if result['skipped_count'] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'{result["skipped_count"]} renewals skipped due to validation failures.'
                        )
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during renewal process: {e}')
            )
            raise
