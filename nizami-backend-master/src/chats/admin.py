from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .models import Chat, Message, MessageFile, MessageLog, MessageStepLog


class MessageFileInline(admin.TabularInline):
    """Inline admin for MessageFile within Message"""
    model = MessageFile
    extra = 0
    readonly_fields = ['id', 'file_name', 'extension', 'size', 'created_at']
    fields = ['id', 'file_name', 'extension', 'size', 'file', 'created_at']
    can_delete = False


class MessageInline(admin.TabularInline):
    """Inline admin for Message within Chat - shows conversation flow"""
    model = Message
    extra = 0
    readonly_fields = ['id', 'uuid', 'role', 'text_preview', 'created_at', 'language']
    fields = ['id', 'role', 'text_preview', 'language', 'created_at']
    can_delete = False
    show_change_link = True
    
    def text_preview(self, obj):
        """Show a preview of the message text"""
        if obj.text:
            preview = obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
            # Color code by role
            if obj.role == 'user':
                return format_html(
                    '<div style="background-color: #e3f2fd; padding: 5px; border-radius: 5px;">'
                    '<strong>👤 User:</strong><br/>{}'
                    '</div>',
                    preview
                )
            elif obj.role == 'ai':
                return format_html(
                    '<div style="background-color: #f1f8e9; padding: 5px; border-radius: 5px;">'
                    '<strong>🤖 AI:</strong><br/>{}'
                    '</div>',
                    preview
                )
            return preview
        return '-'
    text_preview.short_description = 'Message Preview'
    
    def get_queryset(self, request):
        """Order messages by creation time"""
        qs = super().get_queryset(request)
        return qs.order_by('created_at')


class MessageStepLogInline(admin.TabularInline):
    """Inline admin for MessageStepLog within Message"""
    model = MessageStepLog
    extra = 0
    readonly_fields = ['id', 'step_name', 'time_sec', 'created_at']
    fields = ['id', 'step_name', 'time_sec', 'input', 'output', 'created_at']
    can_delete = False
    classes = ['collapse']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """
    Admin interface for Chat model with full CRUD support.
    Includes inline messages to view conversation flow.
    """
    list_display = ['id', 'title', 'user', 'message_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'conversation_view']
    raw_id_fields = ['user']
    inlines = [MessageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'user')
        }),
        ('Conversation', {
            'fields': ('conversation_view',),
            'description': 'View all messages in this chat conversation'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        """Add custom URL for chat log view"""
        urls = super().get_urls()
        custom_urls = [
            path('chat-log/', self.admin_site.admin_view(self.chat_log_view), name='chats_chat_chatlog'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Add link to chat log view"""
        extra_context = extra_context or {}
        extra_context['chat_log_url'] = 'admin:chats_chat_chatlog'
        return super().changelist_view(request, extra_context)
    
    def chat_log_view(self, request):
        """Custom view to show all chat messages (user and AI) across all chats"""
        from django.core.paginator import Paginator
        
        # Get all messages ordered by creation time (newest first)
        messages = Message.objects.select_related('chat', 'chat__user').prefetch_related('messageFiles').order_by('-created_at')
        
        # Filter by role if provided
        role_filter = request.GET.get('role', '')
        if role_filter in ['user', 'ai']:
            messages = messages.filter(role=role_filter)
        
        # Filter by chat if provided
        chat_filter = request.GET.get('chat', '')
        if chat_filter:
            try:
                messages = messages.filter(chat_id=chat_filter)
            except ValueError:
                pass
        
        # Search filter
        search_query = request.GET.get('search', '')
        if search_query:
            messages = messages.filter(text__icontains=search_query)
        
        # Paginate
        paginator = Paginator(messages, 50)  # 50 messages per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'messages': page_obj,
            'role_filter': role_filter,
            'chat_filter': chat_filter,
            'search_query': search_query,
            'opts': self.model._meta,
            'has_view_permission': True,
            'site_header': 'Django administration',
            'site_title': 'Django site admin',
        }
        
        return render(request, 'admin/chats/chat_log.html', context)
    
    def message_count(self, obj):
        """Display the number of messages in the chat"""
        count = obj.messages.count()
        return format_html('<strong>{}</strong>', count)
    message_count.short_description = 'Messages'
    
    def conversation_view(self, obj):
        """Display all messages in a chat-like format"""
        if not obj.pk:
            return "Save the chat first to view messages"
        
        messages = obj.messages.all().order_by('created_at')
        if not messages.exists():
            return "No messages yet"
        
        html = '<div style="max-height: 600px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">'
        
        for msg in messages:
            # Determine styling based on role
            if msg.role == 'user':
                bg_color = '#e3f2fd'
                border_color = '#2196f3'
                icon = '👤'
                label = 'User'
            elif msg.role == 'ai':
                bg_color = '#f1f8e9'
                border_color = '#4caf50'
                icon = '🤖'
                label = 'AI'
            else:
                bg_color = '#fff3e0'
                border_color = '#ff9800'
                icon = '💬'
                label = msg.role.title()
            
            html += f'''
            <div style="margin-bottom: 15px; padding: 10px; background-color: {bg_color}; 
                        border-left: 4px solid {border_color}; border-radius: 5px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <strong>{icon} {label}</strong>
                    <span style="color: #666; font-size: 0.9em;">{msg.created_at.strftime("%Y-%m-%d %H:%M:%S")}</span>
                </div>
                <div style="margin-bottom: 5px;">{msg.text or "<em>No text</em>"}</div>
            '''
            
            if msg.language:
                html += f'<div style="font-size: 0.85em; color: #666;">Language: {msg.language}</div>'
            
            if msg.used_query:
                html += f'<div style="font-size: 0.85em; color: #666; margin-top: 5px;"><strong>Used Query:</strong> {msg.used_query[:100]}...</div>'
            
            if msg.messageFiles.exists():
                files = ', '.join([f.file_name for f in msg.messageFiles.all()])
                html += f'<div style="font-size: 0.85em; color: #666; margin-top: 5px;"><strong>Files:</strong> {files}</div>'
            
            html += f'<div style="font-size: 0.75em; color: #999; margin-top: 5px;">ID: {msg.id} | UUID: {msg.uuid}</div>'
            html += '</div>'
        
        html += '</div>'
        return mark_safe(html)
    conversation_view.short_description = 'Conversation'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Message model with full CRUD support.
    Shows conversation context and related data.
    """
    list_display = ['id', 'chat', 'role_badge', 'text_preview', 'language', 'created_at']
    list_filter = ['role', 'language', 'created_at', 'show_translation_disclaimer']
    search_fields = ['text', 'uuid', 'chat__title', 'used_query']
    readonly_fields = ['id', 'uuid', 'created_at', 'role_badge', 'conversation_context']
    raw_id_fields = ['chat', 'parent']
    inlines = [MessageFileInline, MessageStepLogInline]
    
    def changelist_view(self, request, extra_context=None):
        """Add link to chat log view"""
        extra_context = extra_context or {}
        extra_context['chat_log_url'] = 'admin:chats_chat_chatlog'
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'uuid', 'chat', 'role_badge', 'parent')
        }),
        ('Conversation Context', {
            'fields': ('conversation_context',),
            'description': 'See this message in context with surrounding messages'
        }),
        ('Content', {
            'fields': ('text', 'used_query', 'language')
        }),
        ('Translation', {
            'fields': ('show_translation_disclaimer', 'translation_disclaimer_language'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def role_badge(self, obj):
        """Display role with color coding"""
        if obj.role == 'user':
            return format_html(
                '<span style="background-color: #2196f3; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">👤 USER</span>'
            )
        elif obj.role == 'ai':
            return format_html(
                '<span style="background-color: #4caf50; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">🤖 AI</span>'
            )
        return obj.role
    role_badge.short_description = 'Role'
    
    def text_preview(self, obj):
        """Show a preview of the message text"""
        if obj.text:
            preview = obj.text[:150] + '...' if len(obj.text) > 150 else obj.text
            return preview
        return '-'
    text_preview.short_description = 'Message Text'
    
    def conversation_context(self, obj):
        """Show this message with surrounding messages for context"""
        if not obj.pk or not obj.chat:
            return "Save the message first to view context"
        
        # Get messages from the same chat, ordered by time
        all_messages = obj.chat.messages.all().order_by('created_at')
        messages_list = list(all_messages)
        
        # Find current message index
        try:
            current_idx = messages_list.index(obj)
        except ValueError:
            return "Message not found in chat"
        
        # Get context (2 messages before and after)
        start_idx = max(0, current_idx - 2)
        end_idx = min(len(messages_list), current_idx + 3)
        context_messages = messages_list[start_idx:end_idx]
        
        html = '<div style="max-height: 500px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;">'
        
        for msg in context_messages:
            is_current = msg.id == obj.id
            
            if msg.role == 'user':
                bg_color = '#e3f2fd'
                border_color = '#2196f3'
                icon = '👤'
                label = 'User'
            elif msg.role == 'ai':
                bg_color = '#f1f8e9'
                border_color = '#4caf50'
                icon = '🤖'
                label = 'AI'
            else:
                bg_color = '#fff3e0'
                border_color = '#ff9800'
                icon = '💬'
                label = msg.role.title()
            
            # Highlight current message
            if is_current:
                border_style = '4px solid #ff5722'
                bg_color = '#fff9c4'
            else:
                border_style = f'4px solid {border_color}'
            
            html += f'''
            <div style="margin-bottom: 15px; padding: 10px; background-color: {bg_color}; 
                        border-left: {border_style}; border-radius: 5px; 
                        {"box-shadow: 0 2px 4px rgba(0,0,0,0.2);" if is_current else ""}">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <strong>{icon} {label} {"← CURRENT" if is_current else ""}</strong>
                    <span style="color: #666; font-size: 0.9em;">{msg.created_at.strftime("%H:%M:%S")}</span>
                </div>
                <div style="margin-bottom: 5px;">{msg.text or "<em>No text</em>"}</div>
                <div style="font-size: 0.75em; color: #999;">ID: {msg.id}</div>
            </div>
            '''
        
        html += '</div>'
        return mark_safe(html)
    conversation_context.short_description = 'Conversation Context'


@admin.register(MessageFile)
class MessageFileAdmin(admin.ModelAdmin):
    """
    Admin interface for MessageFile model with full CRUD support.
    """
    list_display = ['id', 'file_name', 'extension', 'size', 'message', 'user', 'created_at']
    list_filter = ['extension', 'created_at']
    search_fields = ['file_name', 'message__uuid', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['message', 'user']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'file_name', 'extension', 'size')
        }),
        ('File', {
            'fields': ('file',)
        }),
        ('Relations', {
            'fields': ('message', 'user')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    """
    Admin interface for MessageLog model with full CRUD support.
    Note: This model uses a custom database ('logs').
    """
    list_display = ['id', 'message', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message__uuid', 'response']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['message']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'message')
        }),
        ('Response', {
            'fields': ('response',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MessageStepLog)
class MessageStepLogAdmin(admin.ModelAdmin):
    """
    Admin interface for MessageStepLog model with full CRUD support.
    """
    list_display = ['id', 'step_name', 'message', 'time_sec', 'created_at']
    list_filter = ['step_name', 'created_at']
    search_fields = ['step_name', 'message__uuid', 'input', 'output']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['message']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'step_name', 'message', 'time_sec')
        }),
        ('Data', {
            'fields': ('input', 'output')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

