from django.contrib import admin
from .models import (
    MoyasarInvoice,
    MoyasarPaymentSource,
    MoyasarPayment,
    MoyasarWebhookEvent,
    UserPaymentSource,
    PaymentUserSubscription
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


@admin.register(PaymentUserSubscription)
class PaymentUserSubscriptionAdmin(admin.ModelAdmin):
    """
    Admin interface for PaymentUserSubscription model with full CRUD support.
    """
    list_display = ['uuid', 'user_subscription', 'payment', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = [
        'uuid',
        'user_subscription__uuid',
        'user_subscription__user__email',
        'user_subscription__user__username',
        'payment__id',
    ]
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    raw_id_fields = ['user_subscription', 'payment']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid',)
        }),
        ('Relations', {
            'fields': ('user_subscription', 'payment'),
            'description': 'Links a payment to a user subscription.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related for better performance.
        """
        qs = super().get_queryset(request)
        return qs.select_related(
            'user_subscription',
            'user_subscription__user',
            'user_subscription__plan',
            'payment',
            'payment__source'
        )
