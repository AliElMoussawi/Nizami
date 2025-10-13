from django.contrib import admin
from .models import (
    MoyasarInvoice,
    MoyasarPaymentSource,
    MoyasarPayment,
    MoyasarWebhookEvent,
    UserPaymentSource
)


@admin.register(MoyasarInvoice)
class MoyasarInvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'amount', 'currency', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['id', 'description']
    readonly_fields = ['internal_uuid', 'id', 'created_at', 'updated_at']


@admin.register(MoyasarPaymentSource)
class MoyasarPaymentSourceAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'type', 'company', 'name', 'number']
    list_filter = ['type', 'company']
    search_fields = ['token', 'name', 'number', 'gateway_id']
    readonly_fields = ['uuid']


@admin.register(MoyasarPayment)
class MoyasarPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'amount', 'currency', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['id', 'description']
    readonly_fields = ['internal_uuid', 'id', 'created_at', 'updated_at']
    raw_id_fields = ['invoice', 'source']


@admin.register(MoyasarWebhookEvent)
class MoyasarWebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'event_type', 'live', 'event_created_at', 'created_at']
    list_filter = ['event_type', 'live', 'created_at']
    search_fields = ['event_id', 'account_name']
    readonly_fields = ['uuid', 'created_at', 'updated_at']


@admin.register(UserPaymentSource)
class UserPaymentSourceAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'user', 'token_type', 'is_default', 'is_active', 'nickname', 'created_at']
    list_filter = ['token_type', 'is_default', 'is_active', 'created_at']
    search_fields = ['user__email', 'user__username', 'token', 'nickname']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'payment_source']
    
    fieldsets = (
        ('User Information', {
            'fields': ('uuid', 'user')
        }),
        ('Payment Details', {
            'fields': ('payment_source', 'token', 'token_type', 'nickname')
        }),
        ('Status', {
            'fields': ('is_default', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        """
        qs = super().get_queryset(request)
        return qs.select_related('user', 'payment_source')
