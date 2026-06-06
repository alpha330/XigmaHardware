import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.market.enums import ReviewStatus


class ProductReview(models.Model):
    """
    ریویو کامل محصول

    ویژگی‌ها:
    - عنوان و متن کامل
    - نقاط قوت و ضعف
    - گالری عکس
    - وضعیت (منتشر شده/مخفی)
    - لایک و دیسلایک
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==================== Relations ====================
    product = models.ForeignKey(
        'market.MarketProduct',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Product')
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('User')
    )

    # ==================== Review Content ====================
    title = models.CharField(_('Title'), max_length=300)

    body = models.TextField(_('Review Body'))

    # نقاط قوت و ضعف
    pros = models.TextField(_('Pros'), blank=True, help_text=_('One per line'))
    cons = models.TextField(_('Cons'), blank=True, help_text=_('One per line'))

    # ==================== Rating (quick) ====================
    rating = models.ForeignKey(
        'market.ProductRating',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name=_('Rating')
    )

    # ==================== Status ====================
    status = models.CharField(
        _('Status'),
        max_length=15,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PUBLISHED
    )

    is_verified_purchase = models.BooleanField(_('Verified Purchase'), default=False)

    # ==================== Engagement ====================
    likes_count = models.PositiveIntegerField(_('Likes'), default=0)
    dislikes_count = models.PositiveIntegerField(_('Dislikes'), default=0)

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_reviews'
        verbose_name = _('Product Review')
        verbose_name_plural = _('Product Reviews')
        unique_together = [['product', 'user']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"📝 {self.title} - {self.product.title[:30]}"

    def get_pros_list(self):
        return [p.strip() for p in self.pros.split('\n') if p.strip()]

    def get_cons_list(self):
        return [c.strip() for c in self.cons.split('\n') if c.strip()]


class ReviewLike(models.Model):
    """لایک/دیسلایک ریویو"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_likes')

    is_like = models.BooleanField(_('Like'), default=True)  # True=Like, False=Dislike

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_likes'
        unique_together = [['review', 'user']]

    def __str__(self):
        return f"{'👍' if self.is_like else '👎'} by {self.user.get_display_name()}"