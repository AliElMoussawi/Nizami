from django.core.management.base import BaseCommand
from src.users.models import User


class Command(BaseCommand):
    help = 'Creates an admin user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Admin email')
        parser.add_argument('--password', type=str, required=True, help='Admin password')
        parser.add_argument('--first-name', type=str, default='Admin', help='First name')
        parser.add_argument('--last-name', type=str, default='User', help='Last name')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        # Check if user already exists
        if User.objects.filter(email__iexact=email.lower()).exists():
            self.stdout.write(self.style.ERROR(f'User with email {email} already exists'))
            return

        # Create the admin user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin',
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Role: {user.role}'))
        self.stdout.write(self.style.SUCCESS(f'Is Staff: {user.is_staff}'))
        self.stdout.write(self.style.SUCCESS(f'Is Superuser: {user.is_superuser}'))

