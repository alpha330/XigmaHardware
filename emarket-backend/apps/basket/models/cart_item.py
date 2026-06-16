import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _


class CartItem(models.Model):
    """
    آیتم‌های داخل سبد خرید
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Relations ====================
    cart = models.ForeignKey(
        'basket.Cart',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Cart')
    )

    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=_('Product'),
        limit_choices_to={
            'is_active': True,
            'is_market_visible': True,
            'market_status': 'published',
            'market_quantity__gt': 0,
        }
    )

    # ==================== Quantity & Price ====================
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        default=1,
    )

    unit_price = models.DecimalField(
        _('Unit Price'),
        max_digits=15,
        decimal_places=2,
        help_text=_('Price at the time of adding to cart')
    )

    # ==================== Status ====================
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        db_index=True
    )

    added_from_wishlist = models.BooleanField(
        _('From Wishlist'),
        default=False
    )

    # ==================== Notes ====================
    notes = models.TextField(_('Notes'), blank=True)

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        ordering = ['-created_at']
        unique_together = [
            ['cart', 'product'],
        ]
        indexes = [
            models.Index(fields=['cart', 'is_active']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.cart}"

    def save(self, *args, **kwargs):
        # 🎯 اگر قیمت واحد خالی بود (مثل زمان ایجاد از طریق پنل ادمین)
        if self.unit_price is None and self.product_id:
            # قیمت را به ترتیب اولویت از محصول می‌خوانیم
            self.unit_price = (
                getattr(self.product, 'final_market_price', None)
                or self.product.market_price
                or self.product.selling_price
                or 0
            )

        super().save(*args, **kwargs)

    # ==================== Properties ====================
    @property
    def total_price(self):
        # 🎯 بررسی می‌کنیم که اگر قیمت واحد یا تعداد خالی بود، کرش نکند و صفر برگرداند
        if self.unit_price is None or self.quantity is None:
            from decimal import Decimal
            return Decimal('0')

        return self.unit_price * self.quantity
    @property
    def market_available(self):
        """موجودی در مارکت"""
        return self.product.market_quantity

    @property
    def is_available(self):
        """آیا محصول هنوز در مارکت موجوده؟"""
        return (
            self.product.is_active and
            self.product.is_market_visible and
            self.product.market_status == 'published' and
            self.product.market_quantity >= self.quantity
        )

    # ==================== Methods ====================
    def update_quantity(self, new_quantity):
        """بروزرسانی تعداد"""
        if new_quantity < 1:
            self.is_active = False
            self.quantity = 0
        else:
            self.quantity = new_quantity

        self.save()
        return self

    def increment(self, amount=1):
        """افزایش تعداد"""
        self.quantity += amount
        self.save(update_fields=['quantity', 'updated_at'])
        return self

    def decrement(self, amount=1):
        """کاهش تعداد"""
        self.quantity = max(1, self.quantity - amount)
        self.save(update_fields=['quantity', 'updated_at'])
        return self

    def remove(self):
        """حذف از سبد (soft delete)"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

