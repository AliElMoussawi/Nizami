import os
import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from src.prompts.enums import PendingDocIntentStatus, PendingDocIntentIntentType
from src.users.models import User


class Chat(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')

    title = models.CharField(max_length=255)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(null=True, blank=True, help_text="Conversation summary maintained throughout the chat")
    summary_last_message_id = models.BigIntegerField(null=True, blank=True, help_text="ID of the last message included in the summary")


class Message(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')

    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=255)
    uuid = models.UUIDField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children')
    language = models.CharField(max_length=255, null=True)
    show_translation_disclaimer = models.BooleanField(default=False)
    translation_disclaimer_language = models.CharField(max_length=255, null=True)

    used_query = models.TextField(null=True)
    metadata_json = models.JSONField(null=True, blank=True)


class MessageFile(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')

    file_name = models.CharField(max_length=255, null=True)
    size = models.PositiveIntegerField()
    extension = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/', null=False, blank=False, serialize=False)

    created_at = models.DateTimeField(auto_now_add=True)

    message = models.ForeignKey(Message, related_name='messageFiles', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, related_name='messageFiles', on_delete=models.CASCADE, null=True)


class MessageAttachment(models.Model):
    """
    Links a message to an uploaded file (uploads.File). Composite unique (message_id, file_id).
    """
    message = models.ForeignKey(Message, related_name='message_attachments', on_delete=models.CASCADE)
    file = models.ForeignKey(
        'uploads.File',
        on_delete=models.CASCADE,
        related_name='message_attachments',
    )

    class Meta:
        db_table = 'chats_message_attachment'
        constraints = [
            models.UniqueConstraint(fields=['message', 'file'], name='chats_message_attachment_message_file_unique'),
        ]


class PendingDocIntent(models.Model):
    """
    Tracks pending final answer when docs are not yet READY; worker posts answer when extraction completes.
    """
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pending_doc_intents', db_column='tenant_id')
    conversation = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='pending_doc_intents')
    user_message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='pending_doc_intents')
    file_ids = models.JSONField(help_text='List of uploads.File UUIDs')
    user_question = models.TextField()
    intent_type = models.CharField(max_length=32, choices=PendingDocIntentIntentType.choices)
    status = models.CharField(
        max_length=32,
        choices=PendingDocIntentStatus.choices,
        default=PendingDocIntentStatus.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chats_pending_doc_intent'
        indexes = [
            models.Index(fields=['tenant', 'status']),
        ]


class LogsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using('logs')


class MessageLog(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    created_at = models.DateTimeField(auto_now_add=True)

    message = models.ForeignKey(Message, related_name='messageLogs', on_delete=models.CASCADE, null=True)
    response = models.TextField(null=True, blank=True)

    logs_objects = LogsManager()

    def response_json(self):
        import ast

        return ast.literal_eval(self.response)


class MessageStepLog(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    created_at = models.DateTimeField(auto_now_add=True)

    step_name = models.CharField(max_length=255, null=True)
    message = models.ForeignKey(Message, related_name='messageStepLogs', on_delete=models.CASCADE, null=True)
    input = models.TextField(null=True, blank=True)
    output = models.TextField(null=True, blank=True)
    time_sec = models.FloatField(null=True, blank=True)

    def __str__(self):
        t = round(self.time_sec, 3)
        return f"{self.id} - {self.step_name} ({t}s)"

    def output_json(self):
        import ast

        return ast.literal_eval(self.output)

    def input_json(self):
        import ast

        return ast.literal_eval(self.output)


@receiver(pre_save, sender=MessageFile)
def modify_file_name(sender, instance, **kwargs):
    if instance.file and instance.file_name is None:
        instance.file_name = instance.file.name
        instance.size = instance.file.size
        instance.extension = os.path.splitext(instance.file.name)[-1].lower().lstrip('.')
        instance.file.name = f"{uuid.uuid4().hex}.{instance.extension}"
