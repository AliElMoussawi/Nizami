# Generated migration for adding summary_last_message_id field to Chat model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0019_chat_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='summary_last_message_id',
            field=models.BigIntegerField(blank=True, help_text='ID of the last message included in the summary', null=True),
        ),
    ]

