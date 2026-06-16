import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.basket.enums import CartType, CartStatus, DiscountType
from .cart_item import CartItem


class Cart(models.Model):
    """
    مدل سبد خرید

    دو نوع سبد:
    ۱. CART (عادی) - قابل پرداخت
    ۲. WISHLIST (آرزوها) - نیاز به تبدیل به CART
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Relations ====================
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name=_('User')
    )

    # ==================== Cart Info ====================
    cart_type = models.CharField(
        _('Cart Type'),
        max_length=10,
        choices=CartType.choices,
        default=CartType.CART,
        db_index=True
    )

    status = models.CharField(
        _('Status'),
        max_length=15,
        choices=CartStatus.choices,
        default=CartStatus.ACTIVE,
        db_index=True
    )

    # ==================== Name (برای سبد آرزوها) ====================
    name = models.CharField(
        _('Wishlist Name'),
        max_length=200,
        blank=True,
        help_text=_('Optional name for wishlist')
    )

    notes = models.TextField(
        _('Notes'),
        blank=True
    )

    # ==================== Discount (فقط برای Wishlist توسط ادمین) ====================
    discount_percent = models.DecimalField(
        _('Discount Percent'),
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_('0-100% discount set by admin/financial')
    )

    discount_amount = models.DecimalField(
        _('Discount Amount'),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_('Fixed discount amount')
    )

    discount_type = models.CharField(
        _('Discount Type'),
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.PERCENT
    )

    discount_set_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discounts_given',
        verbose_name=_('Discount Set By'),
        limit_choices_to={'role__in': ['super_admin', 'accountant']}
    )

    discount_note = models.TextField(
        _('Discount Note'),
        blank=True,
        help_text=_('Reason for discount')
    )

    discount_approved_at = models.DateTimeField(
        _('Discount Approved At'),
        null=True,
        blank=True
    )

    # ==================== Conversion (Wishlist → Cart) ====================
    converted_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_to',
        verbose_name=_('Converted From Wishlist')
    )

    converted_at = models.DateTimeField(
        _('Converted At'),
        null=True,
        blank=True
    )

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    expires_at = models.DateTimeField(
        _('Expires At'),
        null=True,
        blank=True,
        help_text=_('Auto-clean after this date')
    )

    class Meta:
        db_table = 'carts'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'cart_type', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            # هر کاربر فقط یک سبد CART فعال
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(cart_type='cart', status='active'),
                name='unique_active_cart_per_user'
            ),
        ]

    def __str__(self):
        type_icon = '🛒' if self.is_cart else '⭐'
        return f"{type_icon} {self.name or 'Cart'} - {self.user.get_display_name()}"

    # ==================== Properties ====================
    @property
    def is_cart(self):
        return self.cart_type == CartType.CART

    @property
    def is_wishlist(self):
        return self.cart_type == CartType.WISHLIST

    @property
    def can_checkout(self):
        """آیا می‌تونه بره برای پرداخت؟"""
        return self.is_cart and self.status == CartStatus.ACTIVE and self.items.filter(is_active=True).exists()

    @property
    def total_items(self):
        """تعداد کل آیتم‌ها"""
        return self.items.filter(is_active=True).count()

    @property
    def total_quantity(self):
        """تعداد کلی محصولات"""
        return self.items.filter(is_active=True).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def subtotal(self):
        """جمع قیمت قبل از تخفیف"""
        total = Decimal('0')
        for item in self.items.filter(is_active=True).select_related('product'):
            total += item.total_price
        return total

    @property
    def discount_total(self):
        """مقدار تخفیف"""
        if self.discount_percent > 0:
            return self.subtotal * (self.discount_percent / 100)
        elif self.discount_amount > 0:
            return min(self.discount_amount, self.subtotal)
        return Decimal('0')

    @property
    def tax_amount(self):
        """محاسبه مالیات بر ارزش افزوده (۹٪) روی مبلغ بعد از تخفیف"""
        amount_after_discount = max(self.subtotal - self.discount_total, Decimal('0'))
        tax_rate = Decimal('0.09') # نرخ مالیات ۹ درصد
        return amount_after_discount * tax_rate

    @property
    def grand_total(self):
        """جمع نهایی بعد از تخفیف و با احتساب مالیات"""
        amount_after_discount = max(self.subtotal - self.discount_total, Decimal('0'))
        # مالیات را به جمع نهایی اضافه می‌کنیم
        return amount_after_discount + self.tax_amount

    # ==================== Methods ====================
    def convert_to_cart(self):
        """تبدیل Wishlist به Cart"""
        if not self.is_wishlist:
            raise ValueError(_('Only wishlist can be converted to cart.'))

        if self.status != CartStatus.ACTIVE:
            raise ValueError(_('Only active wishlist can be converted.'))

        # غیرفعال کردن سبد CART فعلی (اگر وجود داره)
        Cart.objects.filter(
            user=self.user,
            cart_type=CartType.CART,
            status=CartStatus.ACTIVE
        ).update(status=CartStatus.ABANDONED)

        # ایجاد سبد جدید از روی Wishlist
        cart = Cart.objects.create(
            user=self.user,
            cart_type=CartType.CART,
            status=CartStatus.ACTIVE,
            name=f"From: {self.name or 'Wishlist'}",
            converted_from=self,
            converted_at=models.functions.Now(),
            # انتقال تخفیف
            discount_percent=self.discount_percent,
            discount_amount=self.discount_amount,
            discount_type=self.discount_type,
            discount_set_by=self.discount_set_by,
            discount_note=self.discount_note,
        )

        # کپی آیتم‌ها
        for item in self.items.filter(is_active=True):
            CartItem.objects.create(
                cart=cart,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )

        # آپدیت وضعیت Wishlist
        self.status = CartStatus.CONVERTED
        self.save(update_fields=['status', 'updated_at'])

        return cart

    def set_discount(self, percent=None, amount=None, set_by=None, note=''):
        """تنظیم تخفیف (فقط برای Wishlist توسط ادمین)"""
        if percent is not None:
            if not 0 <= percent <= 100:
                raise ValueError(_('Discount percent must be between 0 and 100.'))
            self.discount_percent = percent
            self.discount_type = DiscountType.PERCENT
        elif amount is not None:
            if amount < 0:
                raise ValueError(_('Discount amount must be positive.'))
            self.discount_amount = amount
            self.discount_type = DiscountType.FIXED

        self.discount_set_by = set_by
        self.discount_note = note
        self.discount_approved_at = models.functions.Now()
        self.save()

    def clear_discount(self):
        """حذف تخفیف"""
        self.discount_percent = 0
        self.discount_amount = 0
        self.discount_set_by = None
        self.discount_note = ''
        self.discount_approved_at = None
        self.save()
