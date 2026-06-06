import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.market.enums import CommentStatus


class ProductComment(models.Model):
    """
    کامنت‌های کاربران روی محصول

    ویژگی‌ها:
    - کامنت اصلی و پاسخ‌ها (threaded)
    - وضعیت (فعال/مخفی/حذف شده)
    - قابلیت گزارش
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==================== Relations ====================
    product = models.ForeignKey(
        'market.MarketProduct',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Product')
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('User')
    )

    # ==================== Threaded ====================
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('Parent Comment')
    )

    # ==================== Content ====================
    body = models.TextField(_('Comment'), max_length=2000)

    # ==================== Status ====================
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=CommentStatus.choices,
        default=CommentStatus.ACTIVE
    )

    is_pinned = models.BooleanField(_('Pinned'), default=False)
    is_edited = models.BooleanField(_('Edited'), default=False)

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_comments'
        verbose_name = _('Product Comment')
        verbose_name_plural = _('Product Comments')
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"💬 {self.body[:50]}... - {self.user.get_display_name()}"

    @property
    def is_reply(self):
        return self.parent is not None

    @property
    def replies_count(self):
        return self.replies.filter(status=CommentStatus.ACTIVE).count()

    def soft_delete(self):
        """حذف نرم"""
        self.status = CommentStatus.DELETED
        self.body = '[deleted]'
        self.save()