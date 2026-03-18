# Chat attachments: Message.metadata_json, MessageAttachment, PendingDocIntent

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0020_chat_summary_last_message_id'),
        ('uploads', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='metadata_json',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_attachments', to='chats.message')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_attachments', to='uploads.file')),
            ],
            options={
                'db_table': 'chats_message_attachment',
            },
        ),
        migrations.AddConstraint(
            model_name='messageattachment',
            constraint=models.UniqueConstraint(fields=('message', 'file'), name='chats_message_attachment_message_file_unique'),
        ),
        migrations.CreateModel(
            name='PendingDocIntent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_ids', models.JSONField(help_text='List of uploads.File UUIDs')),
                ('user_question', models.TextField()),
                ('intent_type', models.CharField(choices=[('SUMMARY', 'Summary'), ('QA', 'Q&A')], max_length=32)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('DONE', 'Done'), ('FAILED', 'Failed')], db_index=True, default='PENDING', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pending_doc_intents', to='chats.chat')),
                ('tenant', models.ForeignKey(db_column='tenant_id', on_delete=django.db.models.deletion.CASCADE, related_name='pending_doc_intents', to=settings.AUTH_USER_MODEL)),
                ('user_message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pending_doc_intents', to='chats.message')),
            ],
            options={
                'db_table': 'chats_pending_doc_intent',
            },
        ),
        migrations.AddIndex(
            model_name='pendingdocintent',
            index=models.Index(fields=['tenant', 'status'], name='chats_pendi_tenant__status_idx'),
        ),
    ]
