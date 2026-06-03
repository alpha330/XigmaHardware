import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class Wishlist(models.Model):
    """
    مدل سبد آرزوها (Wishlist)

    ویژگی‌ها:
    - کاربر می‌تونه چندتا Wishlist داشته باشه
    - هر Wishlist یه اسم داره (مثلاً: "ارتقاء سرور ۱۴۰۳")
    - قابلیت تبدیل به Cart با حفظ تخفیف
    - قابلیت اشتراک‌گذاری (آینده)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Owner ====================
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name=_('User')
    )

    # ==================== Info ====================
    name = models.CharField(
        _('Wishlist Name'),
        max_length=200,
        help_text=_('e.g., "Server Upgrade 1403", "Office Setup"')
    )

    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('Purpose of this wishlist')
    )

    # ==================== Status ====================
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        db_index=True
    )

    is_public = models.BooleanField(
        _('Public'),
        default=False,
        help_text=_('Shareable with others')
    )

    # ==================== Conversion ====================
    can_convert = models.BooleanField(
        _('Can Convert to Cart'),
        default=True,
        help_text=_('If False, admin has blocked conversion')
    )

    conversion_count = models.PositiveIntegerField(
        _('Conversion Count'),
        default=0,
        help_text=_('How many times converted to cart')
    )

    # ==================== Budget ====================
    budget_limit = models.DecimalField(
        _('Budget Limit'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Maximum budget for this wishlist (for estimation)')
    )

    # ==================== Dates ====================
    target_date = models.DateField(
        _('Target Purchase Date'),
        null=True,
        blank=True,
        help_text=_('When user plans to buy')
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    converted_at = models.DateTimeField(_('Last Converted At'), null=True, blank=True)

    class Meta:
        db_table = 'wishlists'
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')
        ordering = ['-updated_at']
        unique_together = [
            ['user', 'name'],  # هر کاربر نمی‌تونه دو Wishlist با اسم یکسان داشته باشه
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active', 'can_convert']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"⭐ {self.name} - {self.user.get_display_name()}"

    # ==================== Properties ====================
    @property
    def total_items(self):
        """تعداد آیتم‌های فعال"""
        return self.cart.items.filter(is_active=True).count() if hasattr(self, 'cart') else 0

    @property
    def total_quantity(self):
        """تعداد کل محصولات"""
        if hasattr(self, 'cart'):
            return self.cart.total_quantity
        return 0

    @property
    def subtotal(self):
        """جمع قیمت قبل از تخفیف"""
        if hasattr(self, 'cart'):
            return self.cart.subtotal
        return 0

    @property
    def estimated_total(self):
        """برآورد قیمت نهایی (با تخفیف)"""
        if hasattr(self, 'cart'):
            return self.cart.grand_total
        return 0

    @property
    def is_over_budget(self):
        """آیا از بودجه بیشتر شده؟"""
        if self.budget_limit and hasattr(self, 'cart'):
            return self.cart.grand_total > self.budget_limit
        return False

    @property
    def budget_remaining(self):
        """بودجه باقی‌مانده"""
        if self.budget_limit and hasattr(self, 'cart'):
            return max(0, self.budget_limit - self.cart.grand_total)
        return None

    # ==================== Methods ====================
    def convert_to_cart(self):
        """تبدیل به سبد خرید واقعی"""
        from apps.basket.models.cart import Cart
        from apps.basket.enums import CartType, CartStatus

        if not self.is_active:
            raise ValueError(_('Wishlist is not active.'))

        if not self.can_convert:
            raise ValueError(_('Conversion is blocked by admin.'))

        # غیرفعال کردن سبد CART فعلی
        Cart.objects.filter(
            user=self.user,
            cart_type=CartType.CART,
            status=CartStatus.ACTIVE
        ).update(status=CartStatus.ABANDONED)

        # ایجاد سبد جدید
        cart = Cart.objects.create(
            user=self.user,
            cart_type=CartType.CART,
            status=CartStatus.ACTIVE,
            name=f"From Wishlist: {self.name}",
            converted_from_wishlist=self,
            # انتقال تخفیف
            discount_percent=self.cart.discount_percent if hasattr(self, 'cart') else 0,
            discount_amount=self.cart.discount_amount if hasattr(self, 'cart') else 0,
            discount_type=self.cart.discount_type if hasattr(self, 'cart') else 'percent',
            discount_set_by=self.cart.discount_set_by if hasattr(self, 'cart') else None,
            discount_note=self.cart.discount_note if hasattr(self, 'cart') else '',
        )

        # کپی آیتم‌ها
        if hasattr(self, 'cart'):
            for item in self.cart.items.filter(is_active=True):
                from apps.basket.models.cart_item import CartItem
                CartItem.objects.create(
                    cart=cart,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    added_from_wishlist=True,
                )

        # آپدیت آمار
        self.conversion_count += 1
        self.converted_at = models.functions.Now()
        self.save(update_fields=['conversion_count', 'converted_at', 'updated_at'])

        return cart

    def toggle_conversion(self, allow=True):
        """فعال/غیرفعال کردن قابلیت تبدیل (توسط ادمین)"""
        self.can_convert = allow
        self.save(update_fields=['can_convert', 'updated_at'])

    def duplicate(self):
        """کپی کردن Wishlist"""
        new_wishlist = Wishlist.objects.create(
            user=self.user,
            name=f"{self.name} (Copy)",
            description=self.description,
            budget_limit=self.budget_limit,
            target_date=self.target_date,
        )

        # کپی آیتم‌ها
        if hasattr(self, 'cart'):
            from apps.basket.models.cart import Cart
            from apps.basket.enums import CartType, CartStatus

            new_cart = Cart.objects.create(
                user=self.user,
                cart_type=CartType.WISHLIST,
                status=CartStatus.ACTIVE,
                name=new_wishlist.name,
            )

            for item in self.cart.items.filter(is_active=True):
                from apps.basket.models.cart_item import CartItem
                CartItem.objects.create(
                    cart=new_cart,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

        return new_wishlist


class WishlistShare(models.Model):
    """
    اشتراک‌گذاری Wishlist با دیگران (آینده)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='shares'
    )

    shared_with = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_wishlists',
        verbose_name=_('Shared With')
    )

    can_edit = models.BooleanField(
        _('Can Edit'),
        default=False
    )

    shared_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shared_wishlists_by_me',
        verbose_name=_('Shared By')
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlist_shares'
        unique_together = ['wishlist', 'shared_with']

    def __str__(self):
        return f"{self.wishlist.name} → {self.shared_with.get_display_name()}"
