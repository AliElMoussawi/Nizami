from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Initialize the vector extension in PostgreSQL'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self.stdout.write(
                    self.style.SUCCESS('Successfully created vector extension')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating vector extension: {e}')
            )



