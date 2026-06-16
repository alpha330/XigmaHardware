import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Coupon(models.Model):
    """
    کوپن تخفیف
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(
        _('Coupon Code'),
        max_length=30,
        unique=True,
        db_index=True,
        help_text=_('Unique code, e.g. WELCOME10')
    )

    DISCOUNT_TYPE_CHOICES = [
        ('percent', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    ]
    discount_type = models.CharField(
        _('Discount Type'),
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent'
    )

    discount_value = models.DecimalField(
        _('Discount Value'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Percentage (1-100) or fixed amount')
    )

    max_uses = models.PositiveIntegerField(
        _('Maximum Uses'),
        default=1,
        help_text=_('0 = unlimited')
    )

    used_count = models.PositiveIntegerField(
        _('Used Count'),
        default=0,
        editable=False
    )

    min_order_amount = models.DecimalField(
        _('Minimum Order Amount'),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_('Minimum invoice total to apply coupon')
    )

    valid_from = models.DateTimeField(_('Valid From'), default=timezone.now)
    valid_to = models.DateTimeField(_('Valid To'))

    is_active = models.BooleanField(_('Active'), default=True, db_index=True)

    description = models.CharField(_('Description'), max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coupons'
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    def is_valid(self, invoice_total=None):
        """بررسی اعتبار کوپن"""
        now = timezone.now()
        if not self.is_active:
            return False, _('Coupon is inactive.')
        if now < self.valid_from:
            return False, _('Coupon is not yet valid.')
        if now > self.valid_to:
            return False, _('Coupon has expired.')
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False, _('Coupon usage limit reached.')
        if invoice_total is not None and invoice_total < self.min_order_amount:
            return False, _(
                f'Minimum order amount is {self.min_order_amount:,} Rials.'
            )
        return True, _('Coupon is valid.')

    def calculate_discount(self, amount):
        """محاسبه مقدار تخفیف"""
        amount = Decimal(str(amount))
        if self.discount_type == 'percent':
            discount = amount * (self.discount_value / 100)
        else:
            discount = min(self.discount_value, amount)
        return discount

    def mark_used(self):
        """افزایش تعداد استفاده"""
        self.used_count += 1
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            self.is_active = False
        self.save(update_fields=['used_count', 'is_active'])