import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class TicketMessage(models.Model):
    """
    پیام‌های داخل تیکت

    هر تیکت می‌تونه چندین پیام داشته باشه
    - پیام کاربر
    - پاسخ پشتیبانی (is_staff_reply)
    - یادداشت داخلی (is_internal_note - فقط برای staff)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Relations ====================
    ticket = models.ForeignKey(
        'support.Ticket',
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Ticket')
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_messages',
        verbose_name=_('Sender')
    )

    # ==================== Content ====================
    body = models.TextField(_('Message'))

    # ==================== Flags ====================
    is_staff_reply = models.BooleanField(
        _('Staff Reply'),
        default=False,
        help_text=_('Is this from support staff?')
    )

    is_internal_note = models.BooleanField(
        _('Internal Note'),
        default=False,
        help_text=_('Visible only to staff')
    )

    is_read = models.BooleanField(
        _('Read'),
        default=False,
        db_index=True
    )

    # ==================== Attachment ====================
    attachment = models.FileField(
        _('Attachment'),
        upload_to='tickets/%Y/%m/',
        null=True,
        blank=True,
        help_text=_('Optional file attachment')
    )

    attachment_name = models.CharField(
        _('Attachment Name'),
        max_length=255,
        blank=True
    )

    # ==================== Metadata ====================
    ip_address = models.GenericIPAddressField(
        _('IP Address'),
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        _('User Agent'),
        blank=True
    )

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'ticket_messages'
        verbose_name = _('Ticket Message')
        verbose_name_plural = _('Ticket Messages')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['ticket', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        sender_type = '👤' if not self.is_staff_reply else '🎧'
        internal = ' 🔒' if self.is_internal_note else ''
        return f"{sender_type}{internal} {self.sender.get_display_name()}: {self.body[:50]}..."

    @property
    def is_visible_to_user(self):
        """آیا کاربر عادی می‌تونه این پیام رو ببینه؟"""
        return not self.is_internal_note

    @property
    def body_short(self):
        """متن کوتاه شده"""
        if self.body:
            return self.body[:100] + '...' if len(self.body) > 100 else self.body
        return ''

    @property
    def sender_type(self):
        """نوع فرستنده"""
        if self.is_internal_note:
            return 'internal_note'
        if self.is_staff_reply:
            return 'staff'
        return 'customer'

    def mark_as_read(self):
        """علامت‌گذاری به عنوان خوانده شده"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def save(self, *args, **kwargs):
        """ذخیره با نام attachment"""
        if self.attachment and not self.attachment_name:
            self.attachment_name = self.attachment.name.split('/')[-1]
        super().save(*args, **kwargs)