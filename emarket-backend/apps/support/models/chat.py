import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.support.enums import ChatStatus


class ChatSession(models.Model):
    """جلسه چت آنلاین"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='agent_chats')

    status = models.CharField(_('Status'), max_length=15, choices=ChatStatus.choices, default=ChatStatus.WAITING)

    subject = models.CharField(_('Subject'), max_length=200, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f"Chat {self.id[:8]} - {self.user.get_display_name()}"


class ChatMessage(models.Model):
    """پیام چت"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField(_('Message'))
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.get_display_name()}: {self.message[:30]}"