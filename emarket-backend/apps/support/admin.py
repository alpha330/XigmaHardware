from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Ticket, TicketMessage, Warranty, ChatSession, ChatMessage, FAQ, FAQCategory
from django.utils import timezone

class TicketMessageInline(admin.TabularInline):
    """پیام‌های تیکت"""
    model = TicketMessage
    extra = 0
    fields = [
        'sender', 'sender_type_badge', 'body_short',
        'is_read', 'attachment_link', 'created_at_jalali',
    ]
    readonly_fields = [
        'sender', 'sender_type_badge', 'body_short',
        'is_read', 'attachment_link', 'created_at_jalali',
    ]
    can_delete = False
    max_num = 0
    ordering = ['created_at']

    def sender_type_badge(self, obj):
        if obj.is_internal_note:
            return format_html('<span style="color:#6f42c1;">🔒 Internal</span>')
        if obj.is_staff_reply:
            return format_html('<span style="color:#17a2b8;">🎧 Staff</span>')
        return format_html('<span style="color:#28a745;">👤 Customer</span>')
    sender_type_badge.short_description = _('Type')

    def body_short(self, obj):
        return obj.body[:100]
    body_short.short_description = _('Message')

    def attachment_link(self, obj):
        if obj.attachment:
            return format_html('<a href="{}" target="_blank">📎 Download</a>', obj.attachment.url)
        return '-'
    attachment_link.short_description = _('Attachment')

    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_jalali.short_description = _('Date')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'ticket_number', 'user_info', 'subject_short',
        'category_badge', 'priority_badge', 'status_badge',
        'assigned_to_info', 'messages_count', 'is_overdue_badge',
        'created_at_jalali',
    ]
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = [
        'ticket_number', 'subject', 'user__email', 'user__mobile',
        'messages__body',
    ]
    readonly_fields = [
        'ticket_number', 'user', 'created_at', 'updated_at', 'resolved_at', 'closed_at',
    ]
    autocomplete_fields = ['user', 'assigned_to', 'order', 'product']

    fieldsets = (
        (_('Ticket Info'), {'fields': ('ticket_number', 'user', 'subject', 'body')}),
        (_('Classification'), {'fields': ('category', 'priority', 'status')}),
        (_('Assignment'), {'fields': ('assigned_to',)}),
        (_('Related'), {'fields': ('order', 'product')}),
        (_('Satisfaction'), {'fields': ('satisfaction_rating', 'satisfaction_comment')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at'), 'classes': ('collapse',)}),
    )

    inlines = [TicketMessageInline]
    list_per_page = 50
    date_hierarchy = 'created_at'

    # ==================== List Display ====================
    @admin.display(description=_('User'))
    def user_info(self, obj):
        return format_html('<b>{}</b><br/><small>{}</small>', obj.user.get_display_name(), obj.user.email or obj.user.mobile or '')

    @admin.display(description=_('Subject'))
    def subject_short(self, obj):
        return obj.subject[:60]

    @admin.display(description=_('Category'))
    def category_badge(self, obj):
        icons = {'order': '📦', 'payment': '💳', 'product': '🔧', 'warranty': '🛡️', 'technical': '⚙️', 'account': '👤', 'shipping': '🚚', 'other': '📋'}
        return format_html('{} {}', icons.get(obj.category, '📋'), obj.get_category_display())

    @admin.display(description=_('Priority'))
    def priority_badge(self, obj):
        colors = {'low': '#28a745', 'medium': '#ffc107', 'high': '#fd7e14', 'urgent': '#dc3545'}
        return format_html('<span style="background:{};color:white;padding:2px 6px;border-radius:4px;font-size:11px;">{}</span>', colors.get(obj.priority, '#6c757d'), obj.get_priority_display())

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {'open': '#ffc107', 'in_progress': '#17a2b8', 'waiting_customer': '#6c757d', 'resolved': '#28a745', 'closed': '#343a40'}
        return format_html('<span style="background:{};color:white;padding:2px 6px;border-radius:4px;font-size:11px;">{}</span>', colors.get(obj.status, '#6c757d'), obj.get_status_display())

    @admin.display(description=_('Assigned'))
    def assigned_to_info(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_display_name()
        return format_html('<span style="color:#dc3545;">Unassigned</span>')

    @admin.display(description=_('Msgs'))
    def messages_count(self, obj):
        return obj.messages_count

    @admin.display(description=_('Overdue'))
    def is_overdue_badge(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color:#dc3545;">⚠️ Overdue</span>')
        return '✅'

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')

    # ==================== Actions ====================
    actions = ['assign_to_me', 'mark_resolved', 'mark_closed', 'reopen_tickets']

    @admin.action(description=_('Assign to me'))
    def assign_to_me(self, request, queryset):
        for ticket in queryset.filter(status__in=['open', 'waiting_customer']):
            ticket.assign_to(request.user)
        self.message_user(request, _(f'{queryset.count()} ticket(s) assigned to you.'))

    @admin.action(description=_('Mark as RESOLVED'))
    def mark_resolved(self, request, queryset):
        for ticket in queryset.filter(status__in=['open', 'in_progress', 'waiting_customer']):
            ticket.resolve()
        self.message_user(request, _('Tickets resolved.'))

    @admin.action(description=_('Mark as CLOSED'))
    def mark_closed(self, request, queryset):
        queryset.filter(status__in=['resolved', 'waiting_customer']).update(status='closed', closed_at=timezone.now())
        self.message_user(request, _('Tickets closed.'))

    @admin.action(description=_('Reopen tickets'))
    def reopen_tickets(self, request, queryset):
        for ticket in queryset.filter(status__in=['resolved', 'closed']):
            ticket.reopen()
        self.message_user(request, _('Tickets reopened.'))


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = ['warranty_number', 'user_info', 'product', 'status_badge', 'start_date', 'end_date', 'days_remaining']
    list_filter = ['status', 'warranty_type']
    search_fields = ['warranty_number', 'serial_number', 'user__email', 'product__name']
    readonly_fields = ['warranty_number', 'created_at', 'updated_at']

    def user_info(self, obj): return obj.user.get_display_name()
    user_info.short_description = _('User')

    def status_badge(self, obj):
        colors = {'active': '#28a745', 'expired': '#6c757d', 'claimed': '#ffc107', 'rejected': '#dc3545', 'completed': '#17a2b8'}
        return format_html('<span style="background:{};color:white;padding:2px 6px;border-radius:4px;">{}</span>', colors.get(obj.status, '#6c757d'), obj.get_status_display())
    status_badge.short_description = _('Status')

    def days_remaining(self, obj): return obj.days_remaining or 0
    days_remaining.short_description = _('Days Left')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id_short', 'user_info', 'agent_info', 'status_badge', 'msg_count', 'started_at']
    list_filter = ['status']
    readonly_fields = ['id', 'user', 'agent', 'started_at', 'ended_at']

    def id_short(self, obj): return str(obj.id)[:8]
    id_short.short_description = _('ID')

    def user_info(self, obj): return obj.user.get_display_name()
    user_info.short_description = _('User')

    def agent_info(self, obj): return obj.agent.get_display_name() if obj.agent else '-'
    agent_info.short_description = _('Agent')

    def status_badge(self, obj):
        colors = {'waiting': '#ffc107', 'active': '#28a745', 'closed': '#6c757d'}
        return format_html('<span style="background:{};color:white;padding:2px 6px;border-radius:4px;">{}</span>', colors.get(obj.status, '#6c757d'), obj.get_status_display())
    status_badge.short_description = _('Status')

    def msg_count(self, obj): return obj.messages.count()
    msg_count.short_description = _('Messages')


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'faqs_count', 'is_active', 'sort_order']
    prepopulated_fields = {'slug': ('name',)}

    def faqs_count(self, obj): return obj.faqs.count()
    faqs_count.short_description = _('FAQs')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question_short', 'category', 'views_count', 'helpful_count', 'is_active', 'sort_order']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']

    def question_short(self, obj): return obj.question[:60]
    question_short.short_description = _('Question')
