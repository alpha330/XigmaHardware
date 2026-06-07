import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.support.enums import TicketStatus, TicketPriority, TicketCategory


class Ticket(models.Model):
    """
    مدل تیکت پشتیبانی

    ویژگی‌ها:
    - شماره تیکت یکتا
    - دسته‌بندی (سفارش، پرداخت، محصول، گارانتی، فنی، ...)
    - اولویت (کم، متوسط، زیاد، فوری)
    - وضعیت (باز، در حال بررسی، منتظر مشتری، حل شده، بسته)
    - قابلیت تخصیص به ادمین
    - پیام‌های چندگانه
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==================== Basic Info ====================
    ticket_number = models.CharField(
        _('Ticket #'),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_('Auto-generated: TKT-XXXXXXXX')
    )

    # ==================== Relations ====================
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_('Customer')
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name=_('Assigned To'),
        limit_choices_to={'is_staff': True}
    )

    # ==================== Classification ====================
    category = models.CharField(
        _('Category'),
        max_length=20,
        choices=TicketCategory.choices,
        default=TicketCategory.OTHER,
        db_index=True
    )

    priority = models.CharField(
        _('Priority'),
        max_length=10,
        choices=TicketPriority.choices,
        default=TicketPriority.MEDIUM,
        db_index=True
    )

    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN,
        db_index=True
    )

    # ==================== Content ====================
    subject = models.CharField(_('Subject'), max_length=300)
    body = models.TextField(_('Description'))

    # ==================== Related Objects ====================
    order = models.ForeignKey(
        'financial.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name=_('Related Order')
    )

    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name=_('Related Product')
    )

    # ==================== Satisfaction ====================
    satisfaction_rating = models.PositiveSmallIntegerField(
        _('Satisfaction Rating'),
        null=True,
        blank=True,
        choices=[(1, '⭐'), (2, '⭐⭐'), (3, '⭐⭐⭐'), (4, '⭐⭐⭐⭐'), (5, '⭐⭐⭐⭐⭐')],
        help_text=_('Customer satisfaction after resolution')
    )

    satisfaction_comment = models.TextField(_('Satisfaction Comment'), blank=True)

    # ==================== Metadata ====================
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    resolved_at = models.DateTimeField(_('Resolved At'), null=True, blank=True)
    closed_at = models.DateTimeField(_('Closed At'), null=True, blank=True)

    class Meta:
        db_table = 'support_tickets'
        verbose_name = _('Support Ticket')
        verbose_name_plural = _('Support Tickets')
        ordering = ['-priority', '-created_at']  # ✅ priority خودش فیلد هست
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"#{self.ticket_number} - {self.subject[:50]}"

    # ==================== Properties ====================
    @property
    def messages_count(self):
        """تعداد پیام‌ها"""
        return self.messages.count()

    @property
    def user_messages_count(self):
        """پیام‌های کاربر"""
        return self.messages.filter(is_staff_reply=False, is_internal_note=False).count()

    @property
    def staff_messages_count(self):
        """پاسخ‌های پشتیبانی"""
        return self.messages.filter(is_staff_reply=True, is_internal_note=False).count()

    @property
    def last_message(self):
        """آخرین پیام"""
        return self.messages.last()

    @property
    def last_activity(self):
        """آخرین فعالیت"""
        last_msg = self.messages.last()
        return last_msg.created_at if last_msg else self.updated_at

    @property
    def is_overdue(self):
        """آیا overdue شده؟"""
        from datetime import timedelta
        if self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]:
            deadline = self.created_at + timedelta(hours=24 if self.priority == TicketPriority.URGENT else 72)
            return timezone.now() > deadline
        return False

    @property
    def priority_order(self):
        """اولویت عددی برای مرتب‌سازی"""
        order = {
            TicketPriority.URGENT: 0,
            TicketPriority.HIGH: 1,
            TicketPriority.MEDIUM: 2,
            TicketPriority.LOW: 3,
        }
        return order.get(self.priority, 2)

    # ==================== Methods ====================
    def assign_to(self, staff_user):
        """تخصیص به پشتیبان"""
        self.assigned_to = staff_user
        self.status = TicketStatus.IN_PROGRESS
        self.save(update_fields=['assigned_to', 'status', 'updated_at'])

    def resolve(self):
        """حل کردن تیکت"""
        self.status = TicketStatus.RESOLVED
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at', 'updated_at'])

    def close(self):
        """بستن تیکت"""
        self.status = TicketStatus.CLOSED
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at', 'updated_at'])

    def reopen(self):
        """بازگشایی مجدد"""
        self.status = TicketStatus.OPEN
        self.resolved_at = None
        self.closed_at = None
        self.save(update_fields=['status', 'resolved_at', 'closed_at', 'updated_at'])

    def add_message(self, sender, body, is_staff=False, is_internal=False, attachment=None, ip=None):
        """افزودن پیام به تیکت"""
        msg = self.messages.create(
            sender=sender,
            body=body,
            is_staff_reply=is_staff,
            is_internal_note=is_internal,
            attachment=attachment,
            ip_address=ip,
        )

        # بروزرسانی وضعیت
        if is_staff and self.status == TicketStatus.OPEN:
            self.status = TicketStatus.IN_PROGRESS
        elif not is_staff and self.status == TicketStatus.WAITING_CUSTOMER:
            self.status = TicketStatus.IN_PROGRESS
        elif not is_staff and self.status == TicketStatus.RESOLVED:
            self.reopen()

        self.save(update_fields=['status', 'updated_at'])

        return msg

    def save(self, *args, **kwargs):
        """تولید شماره تیکت خودکار"""
        if not self.ticket_number:
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)