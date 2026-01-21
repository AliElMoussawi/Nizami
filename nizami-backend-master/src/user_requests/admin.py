from django.contrib import admin
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html

from src.user_requests.enums import LegalAssistanceRequestStatus
from src.user_requests.models import LegalAssistanceRequest


@admin.register(LegalAssistanceRequest)
class LegalAssistanceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_email',
        'user_phone_display',
        'chat_title',
        'status_badge',
        'in_charge_display',
        'created_at_ts',
        'in_progress_ts',
        'closed_at_ts',
    ]
    list_filter = ['status', 'created_at_ts']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'chat__title', 'in_charge']
    readonly_fields = ['created_at_ts', 'in_progress_ts', 'closed_at_ts', 'chat_summary_display', 'user_link', 'chat_link']
    raw_id_fields = ['user', 'chat']
    ordering = ['-created_at_ts']
    date_hierarchy = 'created_at_ts'
    actions = ['mark_in_progress_action', 'mark_closed_action']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user_link', 'user', 'chat_link', 'chat', 'status', 'in_charge'),
        }),
        ('Timestamps', {
            'fields': ('created_at_ts', 'in_progress_ts', 'closed_at_ts')
        }),
        ('Chat Summary', {
            'fields': ('chat_summary_display',),
            'classes': ('wide',),
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def user_phone_display(self, obj):
        phone = getattr(obj.user, 'phone', None) or getattr(obj.user, 'phone_number', None)
        return phone or '-'
    user_phone_display.short_description = 'User Phone'
    
    def chat_title(self, obj):
        return obj.chat.title
    chat_title.short_description = 'Chat Title'
    chat_title.admin_order_field = 'chat__title'
    
    def chat_summary_display(self, obj):
        summary = obj.chat.summary or 'No summary available'
        return format_html(
            '<div style="max-width: 100%; white-space: pre-wrap; font-size: 14px; line-height: 1.6; padding: 15px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;">{}</div>',
            summary
        )
    chat_summary_display.short_description = 'Chat Summary'
    
    def in_charge_display(self, obj):
        return obj.in_charge or '-'
    in_charge_display.short_description = 'In Charge'
    in_charge_display.admin_order_field = 'in_charge'
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    user_link.short_description = 'User'
    
    def chat_link(self, obj):
        if obj.chat:
            url = reverse('admin:chats_chat_change', args=[obj.chat.pk])
            return format_html('<a href="{}">{}</a>', url, f"Chat {obj.chat.id} - {obj.chat.title}")
        return '-'
    chat_link.short_description = 'Chat'
    
    def status_badge(self, obj):
        return obj.status.replace('_', ' ').title()
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'chat')
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'mark_in_progress_action' in actions:
            pass
        return actions
    
    def mark_in_progress_action(self, request, queryset):
        queryset = queryset.exclude(status=LegalAssistanceRequestStatus.CLOSED.value)
        
        if not queryset.exists():
            self.message_user(request, "No valid requests selected. Closed requests cannot be marked as in progress.", messages.WARNING)
            return
        
        updated = 0
        errors = []
        
        for obj in queryset:
            if obj.status == LegalAssistanceRequestStatus.NEW.value:
                if not obj.in_charge:
                    errors.append(f"Request #{obj.id}: 'In Charge' field is required when moving to In Progress status.")
                    continue
                obj.mark_in_progress()
                updated += 1
            else:
                errors.append(f"Request #{obj.id}: Can only mark 'New' requests as 'In Progress'.")
        
        if updated > 0:
            self.message_user(request, f"Successfully marked {updated} request(s) as in progress.", messages.SUCCESS)
        if errors:
            for error in errors:
                self.message_user(request, error, messages.ERROR)
    
    mark_in_progress_action.short_description = "Mark selected requests as In Progress"
    
    def mark_closed_action(self, request, queryset):
        updated = 0
        errors = []
        
        for obj in queryset:
            if obj.status == LegalAssistanceRequestStatus.CLOSED.value:
                errors.append(f"Request #{obj.id}: Already closed.")
                continue
            
            if not obj.in_charge:
                errors.append(f"Request #{obj.id}: 'In Charge' field is required when moving to Closed status.")
                continue
            
            obj.mark_closed()
            updated += 1
        
        if updated > 0:
            self.message_user(request, f"Successfully marked {updated} request(s) as closed.", messages.SUCCESS)
        if errors:
            for error in errors:
                self.message_user(request, error, messages.ERROR)
    
    mark_closed_action.short_description = "Mark selected requests as Closed"
    
    def save_model(self, request, obj, form, change):
        if change and obj.pk:
            original = LegalAssistanceRequest.objects.get(pk=obj.pk)
            original_status = original.status
            new_status = obj.status
            
            if original_status != new_status:
                if original_status == LegalAssistanceRequestStatus.NEW.value and new_status == LegalAssistanceRequestStatus.IN_PROGRESS.value:
                    if not obj.in_charge or not obj.in_charge.strip():
                        self.message_user(request, "Error: 'In Charge' field is required when moving from New to In Progress status.", messages.ERROR)
                        raise ValueError("In Charge field is required when moving to In Progress status")
                    obj.mark_in_progress(obj.in_charge)
                    return
                
                elif original_status == LegalAssistanceRequestStatus.IN_PROGRESS.value and new_status == LegalAssistanceRequestStatus.CLOSED.value:
                    if not obj.in_charge or not obj.in_charge.strip():
                        self.message_user(request, "Error: 'In Charge' field is required when moving from In Progress to Closed status.", messages.ERROR)
                        raise ValueError("In Charge field is required when moving to Closed status")
                    obj.mark_closed(obj.in_charge)
                    return
                
                elif original_status == LegalAssistanceRequestStatus.NEW.value and new_status == LegalAssistanceRequestStatus.CLOSED.value:
                    if not obj.in_charge or not obj.in_charge.strip():
                        self.message_user(request, "Error: 'In Charge' field is required when moving to Closed status.", messages.ERROR)
                        raise ValueError("In Charge field is required when moving to Closed status")
                    obj.mark_in_progress(obj.in_charge)
                    obj.mark_closed(obj.in_charge)
                    return
        
        super().save_model(request, obj, form, change)