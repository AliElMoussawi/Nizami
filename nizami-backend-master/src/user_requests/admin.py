from django.contrib import admin
from django.utils.html import format_html

from src.user_requests.models import LegalAssistanceRequest


@admin.register(LegalAssistanceRequest)
class LegalAssistanceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_email',
        'user_phone_display',
        'chat_title',
        'status_badge',
        'created_at_ts',
        'in_progress_ts',
        'closed_at_ts',
    ]
    list_filter = ['status', 'created_at_ts']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'chat__title']
    readonly_fields = ['created_at_ts', 'in_progress_ts', 'closed_at_ts', 'chat_summary_display']
    ordering = ['-created_at_ts']
    date_hierarchy = 'created_at_ts'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'chat', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at_ts', 'in_progress_ts', 'closed_at_ts')
        }),
        ('Chat Summary', {
            'fields': ('chat_summary_display',),
            'classes': ('wide',)
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
        return format_html('<div style="max-width: 600px; white-space: pre-wrap;">{}</div>', summary)
    chat_summary_display.short_description = 'Chat Summary'
    
    def status_badge(self, obj):
        colors = {
            'new': '#3b82f6',  # blue
            'in_progress': '#f59e0b',  # yellow
            'closed': '#10b981',  # green
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; text-transform: capitalize;">{}</span>',
            color,
            obj.status.replace('_', ' ')
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'chat')
