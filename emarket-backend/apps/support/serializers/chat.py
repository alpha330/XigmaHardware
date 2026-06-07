from rest_framework import serializers
from apps.support.models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """پیام چت"""
    sender_name = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'is_mine', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.get_display_name()

    def get_is_mine(self, obj):
        request = self.context.get('request')
        return request and obj.sender == request.user


class ChatSessionSerializer(serializers.ModelSerializer):
    """جلسه چت"""
    user_name = serializers.SerializerMethodField()
    agent_name = serializers.SerializerMethodField()
    messages = ChatMessageSerializer(many=True, read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            'id', 'user', 'user_name', 'agent', 'agent_name',
            'status', 'subject', 'unread_count',
            'messages',
            'started_at', 'ended_at',
        ]

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def get_agent_name(self, obj):
        return obj.agent.get_display_name() if obj.agent else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class ChatStartSerializer(serializers.Serializer):
    """شروع چت"""
    subject = serializers.CharField(required=False, allow_blank=True, max_length=200)
    message = serializers.CharField(required=True)

    def validate_message(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Message must be at least 2 characters.')
        return value