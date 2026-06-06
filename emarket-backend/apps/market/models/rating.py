import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
from apps.market.enums import RatingCategory


class ProductRating(models.Model):
    """
    امتیازدهی کاربران به محصول

    چهار محور:
    1. ارزش خرید (Value for Money)
    2. کیفیت محصول (Quality)
    3. کارایی (Performance)
    4. امتیاز کلی (Overall)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==================== Relations ====================
    product = models.ForeignKey(
        'market.MarketProduct',
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('Product')
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('User')
    )

    # ==================== Ratings (1-5) ====================
    value_for_money = models.PositiveSmallIntegerField(
        _('Value for Money'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('1-5: How worth is the price?')
    )

    quality = models.PositiveSmallIntegerField(
        _('Product Quality'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('1-5: Build and material quality')
    )

    performance = models.PositiveSmallIntegerField(
        _('Performance'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('1-5: Speed, efficiency, reliability')
    )

    overall = models.PositiveSmallIntegerField(
        _('Overall Rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('1-5: Overall satisfaction')
    )

    # ==================== Status ====================
    is_active = models.BooleanField(_('Active'), default=True)
    is_verified_purchase = models.BooleanField(
        _('Verified Purchase'),
        default=False,
        help_text=_('User actually bought this product')
    )

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_ratings'
        verbose_name = _('Product Rating')
        verbose_name_plural = _('Product Ratings')
        unique_together = [['product', 'user']]  # هر کاربر فقط یه بار
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"⭐ {self.overall}/5 - {self.product.title[:50]} by {self.user.get_display_name()}"

    @property
    def average_score(self):
        """میانگین امتیازات"""
        return round((self.value_for_money + self.quality + self.performance + self.overall) / 4, 1)