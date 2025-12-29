from django.contrib import admin
from .models import Prompt


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    """
    Admin interface for Prompt model with full CRUD support.
    """
    list_display = ['id', 'title', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'name', 'description']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'name', 'description')
        }),
        ('Prompt Value', {
            'fields': ('value',),
            'description': 'The actual prompt template. Use {context} and {language} as placeholders.'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make 'name' readonly when editing existing prompt to prevent breaking references.
        """
        if obj:  # editing an existing object
            return list(self.readonly_fields) + ['name']
        return self.readonly_fields

