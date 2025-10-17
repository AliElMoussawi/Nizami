from django.contrib import admin
from .models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'tier', 
        'price_display', 
        'interval_display',
        'credit_type',
        'credit_amount',
        'is_unlimited',
        'is_deleted',
        'created_at'
    )
    list_filter = (
        'tier', 
        'is_active', 
        'credit_type', 
        'is_unlimited',
        'interval_unit',
        'rollover_allowed',
        'created_at'
    )
    search_fields = ('name', 'description', 'uuid')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'name', 'tier', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price_cents', 'currency', 'interval_unit', 'interval_count')
        }),
        ('Credits', {
            'fields': ('credit_type', 'credit_amount', 'is_unlimited', 'rollover_allowed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Display price in a readable format"""
        price = obj.price_cents / 100
        return f"{obj.currency} {price:.2f}"
    price_display.short_description = 'Price'
    
    def interval_display(self, obj):
        """Display interval in readable format"""
        if obj.interval_count == 1:
            return obj.get_interval_unit_display()
        return f"{obj.interval_count} {obj.get_interval_unit_display()}s"
    interval_display.short_description = 'Billing Interval'
