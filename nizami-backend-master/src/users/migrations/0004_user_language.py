# Generated migration for adding language field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_user_jurisdiction'),  # Replace with your latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(
                choices=[('en', 'English'), ('ar', 'Arabic')],
                default='ar',
                max_length=10
            ),
        ),
    ]
