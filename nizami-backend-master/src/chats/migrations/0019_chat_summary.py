# Generated migration for adding summary field to Chat model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0018_alter_messagesteplog_time_sec'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='summary',
            field=models.TextField(blank=True, help_text='Conversation summary maintained throughout the chat', null=True),
        ),
    ]

