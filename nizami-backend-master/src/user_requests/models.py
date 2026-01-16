from django.db import models
from django.utils import timezone

from src.chats.models import Chat
from src.user_requests.enums import LegalAssistanceRequestStatus
from src.users.models import User


class LegalAssistanceRequest(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='legal_assistance_requests')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='legal_assistance_requests')
    
    status = models.CharField(
        max_length=20,
        choices=[(status.value, status.name) for status in LegalAssistanceRequestStatus],
        default=LegalAssistanceRequestStatus.NEW.value
    )
    
    in_charge = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name of the admin/person in charge of this request. Required when moving to in_progress or closed."
    )
    
    created_at_ts = models.DateTimeField(auto_now_add=True)
    in_progress_ts = models.DateTimeField(null=True, blank=True)
    closed_at_ts = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at_ts']
        verbose_name = 'Legal Assistance Request'
        verbose_name_plural = 'Legal Assistance Requests'

    def __str__(self):
        return f"LegalAssistanceRequest {self.id} - {self.user.email} - {self.status}"

    def mark_in_progress(self, in_charge=None):
        """Mark the request as in progress"""
        if self.status == LegalAssistanceRequestStatus.NEW.value:
            if in_charge:
                self.in_charge = in_charge
            self.status = LegalAssistanceRequestStatus.IN_PROGRESS.value
            self.in_progress_ts = timezone.now()
            update_fields = ['status', 'in_progress_ts']
            if in_charge:
                update_fields.append('in_charge')
            self.save(update_fields=update_fields)

    def mark_closed(self, in_charge=None):
        """Mark the request as closed"""
        if self.status != LegalAssistanceRequestStatus.CLOSED.value:
            if in_charge:
                self.in_charge = in_charge
            self.status = LegalAssistanceRequestStatus.CLOSED.value
            self.closed_at_ts = timezone.now()
            update_fields = ['status', 'closed_at_ts']
            if in_charge:
                update_fields.append('in_charge')
            self.save(update_fields=update_fields)
