from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.support.models import Ticket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    """پیام تیکت"""
    sender_name = serializers.SerializerMethodField()
    is_staff = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = [
            'id', 'sender', 'sender_name', 'is_staff',
            'body', 'is_staff_reply', 'is_internal_note',
            'attachment', 'created_at',
        ]
        read_only_fields = ['id', 'sender', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_display_name()

    def get_is_staff(self, obj):
        return obj.sender.is_staff or obj.sender.is_superuser


class TicketListSerializer(serializers.ModelSerializer):
    """لیست تیکت‌ها"""
    user_name = serializers.SerializerMethodField()
    messages_count = serializers.IntegerField(read_only=True)
    last_message = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'user_name', 'subject',
            'category', 'priority', 'priority_display',
            'status', 'status_display',
            'messages_count', 'last_message',
            'assigned_to', 'created_at', 'updated_at',
        ]

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def get_last_message(self, obj):
        last = obj.messages.last()
        if last:
            return {
                'sender': last.sender.get_display_name(),
                'body': last.body[:100],
                'created_at': last.created_at,
            }
        return None

    def get_status_display(self, obj):
        colors = {
            'open': 'warning', 'in_progress': 'info',
            'waiting_customer': 'secondary', 'resolved': 'success', 'closed': 'dark',
        }
        return {'code': obj.status, 'label': obj.get_status_display(), 'color': colors.get(obj.status, 'secondary')}

    def get_priority_display(self, obj):
        icons = {'low': '🟢', 'medium': '🟡', 'high': '🟠', 'urgent': '🔴'}
        return {'code': obj.priority, 'label': obj.get_priority_display(), 'icon': icons.get(obj.priority, '⚪')}


class TicketSerializer(serializers.ModelSerializer):
    """جزئیات کامل تیکت"""
    user_name = serializers.SerializerMethodField()
    messages = TicketMessageSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'user', 'user_name',
            'category', 'priority', 'priority_display',
            'status', 'status_display',
            'subject', 'body',
            'assigned_to', 'assigned_to_name',
            'order', 'product',
            'messages',
            'created_at', 'updated_at', 'resolved_at',
        ]
        read_only_fields = ['id', 'ticket_number', 'user', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def get_status_display(self, obj):
        return {'code': obj.status, 'label': obj.get_status_display()}

    def get_priority_display(self, obj):
        return {'code': obj.priority, 'label': obj.get_priority_display()}

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_display_name() if obj.assigned_to else None


class TicketCreateSerializer(serializers.ModelSerializer):
    """ایجاد تیکت"""

    class Meta:
        model = Ticket
        fields = ['category', 'priority', 'subject', 'body', 'order', 'product']

    def validate_subject(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(_('Subject must be at least 5 characters.'))
        return value

    def validate_body(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError(_('Description must be at least 20 characters.'))
        return value


class TicketStatusSerializer(serializers.Serializer):
    """تغییر وضعیت تیکت"""
    status = serializers.ChoiceField(choices=['in_progress', 'waiting_customer', 'resolved', 'closed'])
    note = serializers.CharField(required=False, allow_blank=True)


class TicketReplySerializer(serializers.Serializer):
    """پاسخ به تیکت"""
    body = serializers.CharField(required=True)
    is_internal_note = serializers.BooleanField(default=False)
    attachment = serializers.FileField(required=False)

    def validate_body(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(_('Message must be at least 2 characters.'))
        return value