import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.basket.models import Cart, CartItem
from apps.basket.enums import CartType, CartStatus, DiscountType

logger = logging.getLogger(__name__)


class CartService:
    """
    سرویس مدیریت سبد خرید

    عملیات‌های اصلی:
    - ایجاد/دریافت سبد فعال
    - افزودن محصول
    - بروزرسانی تعداد
    - حذف آیتم
    - محاسبه قیمت‌ها
    - اعتبارسنجی موجودی
    - تبدیل Wishlist به Cart
    """

    @classmethod
    def get_or_create_cart(cls, user, cart_type=CartType.CART):
        """
        دریافت یا ایجاد سبد خرید فعال

        Args:
            user: کاربر
            cart_type: نوع سبد (CART یا WISHLIST)

        Returns:
            Cart: سبد خرید
        """
        cart, created = Cart.objects.get_or_create(
            user=user,
            cart_type=cart_type,
            status=CartStatus.ACTIVE,
            defaults={
                'name': 'My Cart' if cart_type == CartType.CART else 'My Wishlist',
            }
        )

        if created:
            logger.info(f"New {cart_type} created for user {user.email or user.mobile}")

        return cart

    @classmethod
    @transaction.atomic
    def add_item(cls, cart, product, quantity=1, notes=''):
        """
        افزودن محصول به سبد خرید

        Args:
            cart: سبد خرید
            product: محصول
            quantity: تعداد
            notes: یادداشت

        Returns:
            tuple: (CartItem, created)
        """
        # اعتبارسنجی محصول
        cls._validate_product_availability(product, quantity)

        # ایجاد یا بروزرسانی آیتم
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': product.final_market_price,
                'notes': notes,
                'is_active': True,
            }
        )

        if not created:
            # اگر قبلاً بود و غیرفعال بود، فعالش کن
            if not item.is_active:
                item.is_active = True
                item.quantity = quantity
            else:
                item.quantity += quantity

            # آپدیت قیمت (ممکنه تغییر کرده باشه)
            item.unit_price = product.final_market_price
            item.notes = notes if notes else item.notes
            item.save()

        logger.info(
            f"Added to cart {cart.id}: {product.sku} x{quantity} "
            f"({'new' if created else 'updated'})"
        )

        return item, created

    @classmethod
    @transaction.atomic
    def update_quantity(cls, item, quantity):
        """
        بروزرسانی تعداد آیتم

        Args:
            item: CartItem
            quantity: تعداد جدید

        Returns:
            CartItem
        """
        if quantity < 0:
            raise ValueError(_('Quantity must be positive.'))

        if quantity == 0:
            item.remove()
            logger.info(f"Item {item.id} removed (quantity=0)")
            return item

        # چک موجودی
        if quantity > item.product.market_quantity:
            raise ValueError(
                _(f'Only {item.product.market_quantity} available in market.')
            )

        item.quantity = quantity
        item.save(update_fields=['quantity', 'updated_at'])

        logger.info(f"Item {item.id} quantity updated to {quantity}")

        return item

    @classmethod
    @transaction.atomic
    def remove_item(cls, item):
        """
        حذف آیتم از سبد (soft delete)

        Args:
            item: CartItem
        """
        item.remove()
        logger.info(f"Item {item.id} removed from cart {item.cart.id}")

    @classmethod
    @transaction.atomic
    def remove_items(cls, cart, item_ids):
        """
        حذف گروهی آیتم‌ها

        Args:
            cart: سبد خرید
            item_ids: لیست شناسه‌های آیتم

        Returns:
            int: تعداد آیتم‌های حذف شده
        """
        count = cart.items.filter(
            id__in=item_ids,
            is_active=True
        ).update(is_active=False, updated_at=timezone.now())

        logger.info(f"Removed {count} items from cart {cart.id}")

        return count

    @classmethod
    @transaction.atomic
    def clear_cart(cls, cart):
        """
        خالی کردن کل سبد

        Args:
            cart: سبد خرید

        Returns:
            int: تعداد آیتم‌های حذف شده
        """
        count = cart.items.filter(is_active=True).update(
            is_active=False,
            updated_at=timezone.now()
        )

        logger.info(f"Cart {cart.id} cleared: {count} items removed")

        return count

    @classmethod
    @transaction.atomic
    def convert_wishlist_to_cart(cls, wishlist_cart):
        """
        تبدیل سبد آرزو به سبد خرید واقعی

        Args:
            wishlist_cart: سبد از نوع WISHLIST

        Returns:
            Cart: سبد خرید جدید
        """
        if wishlist_cart.cart_type != CartType.WISHLIST:
            raise ValueError(_('Only wishlist can be converted.'))

        if wishlist_cart.status != CartStatus.ACTIVE:
            raise ValueError(_('Only active wishlist can be converted.'))

        # اعتبارسنجی آیتم‌ها
        unavailable = []
        for item in wishlist_cart.items.filter(is_active=True):
            if not item.is_available:
                unavailable.append(item.product.name)

        if unavailable:
            raise ValueError(
                _(f'Some items are unavailable: {", ".join(unavailable)}')
            )

        # غیرفعال کردن سبد CART فعلی
        Cart.objects.filter(
            user=wishlist_cart.user,
            cart_type=CartType.CART,
            status=CartStatus.ACTIVE
        ).update(status=CartStatus.ABANDONED)

        # ایجاد سبد جدید
        new_cart = Cart.objects.create(
            user=wishlist_cart.user,
            cart_type=CartType.CART,
            status=CartStatus.ACTIVE,
            name=f"From Wishlist: {wishlist_cart.name}",
            converted_from=wishlist_cart,
            converted_at=timezone.now(),
            discount_percent=wishlist_cart.discount_percent,
            discount_amount=wishlist_cart.discount_amount,
            discount_type=wishlist_cart.discount_type,
            discount_set_by=wishlist_cart.discount_set_by,
            discount_note=wishlist_cart.discount_note,
        )

        # کپی آیتم‌ها
        for item in wishlist_cart.items.filter(is_active=True):
            CartItem.objects.create(
                cart=new_cart,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.final_market_price,  # قیمت روز
                added_from_wishlist=True,
                notes=item.notes,
            )

        # آپدیت وضعیت Wishlist
        wishlist_cart.status = CartStatus.CONVERTED
        wishlist_cart.save(update_fields=['status', 'updated_at'])

        logger.info(
            f"Wishlist {wishlist_cart.id} converted to Cart {new_cart.id} "
            f"with {new_cart.total_items} items"
        )

        return new_cart

    @classmethod
    @transaction.atomic
    def apply_discount(cls, cart, percent=None, amount=None, set_by=None, note=''):
        """
        اعمال تخفیف روی سبد (فقط برای Wishlist)

        Args:
            cart: سبد (WISHLIST)
            percent: درصد تخفیف (0-100)
            amount: مبلغ تخفیف
            set_by: تنظیم‌کننده (ادمین)
            note: توضیحات

        Returns:
            Cart
        """
        if not cart.is_wishlist:
            raise ValueError(_('Discount can only be applied to wishlist.'))

        if percent is not None:
            if not 0 <= percent <= 100:
                raise ValueError(_('Percent must be between 0 and 100.'))
            cart.discount_percent = percent
            cart.discount_type = DiscountType.PERCENT
        elif amount is not None:
            if amount < 0:
                raise ValueError(_('Amount must be positive.'))
            if amount > cart.subtotal:
                raise ValueError(_('Discount cannot exceed cart total.'))
            cart.discount_amount = amount
            cart.discount_type = DiscountType.FIXED
        else:
            raise ValueError(_('Either percent or amount is required.'))

        cart.discount_set_by = set_by
        cart.discount_note = note
        cart.discount_approved_at = timezone.now()
        cart.save()

        logger.info(
            f"Discount applied to {cart.id}: "
            f"{'%' + str(percent) if percent else str(amount)} "
            f"by {set_by.get_display_name() if set_by else 'system'}"
        )

        return cart

    @classmethod
    @transaction.atomic
    def remove_discount(cls, cart):
        """
        حذف تخفیف از سبد

        Args:
            cart: سبد

        Returns:
            Cart
        """
        cart.discount_percent = 0
        cart.discount_amount = 0
        cart.discount_set_by = None
        cart.discount_note = ''
        cart.discount_approved_at = None
        cart.save()

        logger.info(f"Discount removed from cart {cart.id}")

        return cart

    @classmethod
    def get_cart_summary(cls, cart):
        """
        دریافت خلاصه سبد خرید

        Args:
            cart: سبد خرید

        Returns:
            dict
        """
        items = cart.items.filter(is_active=True).select_related('product__brand')

        unavailable_items = []
        for item in items:
            if not item.is_available:
                unavailable_items.append({
                    'id': str(item.id),
                    'product_name': item.product.name,
                    'requested': item.quantity,
                    'available': item.product.market_quantity,
                })

        return {
            'cart_id': str(cart.id),
            'cart_type': cart.cart_type,
            'status': cart.status,
            'total_items': cart.total_items,
            'total_quantity': cart.total_quantity,
            'subtotal': float(cart.subtotal),
            'discount_total': float(cart.discount_total),
            'grand_total': float(cart.grand_total),
            'has_discount': cart.discount_percent > 0 or cart.discount_amount > 0,
            'discount_percent': float(cart.discount_percent),
            'can_checkout': cart.can_checkout,
            'unavailable_items': unavailable_items,
            'items_count': items.count(),
        }

    @classmethod
    def validate_cart_for_checkout(cls, cart):
        """
        اعتبارسنجی سبد قبل از پرداخت

        Args:
            cart: سبد خرید

        Returns:
            dict: نتیجه اعتبارسنجی
        """
        errors = []
        warnings = []

        # چک نوع سبد
        if not cart.is_cart:
            errors.append(_('Only shopping cart can proceed to checkout.'))

        # چک وضعیت
        if cart.status != CartStatus.ACTIVE:
            errors.append(_('Cart is not active.'))

        # چک آیتم‌ها
        if not cart.items.filter(is_active=True).exists():
            errors.append(_('Cart is empty.'))

        # چک موجودی
        for item in cart.items.filter(is_active=True):
            if not item.is_available:
                errors.append(
                    _(f'{item.product.name}: requested {item.quantity}, available {item.product.market_quantity}')
                )
            elif item.quantity > item.product.market_quantity:
                warnings.append(
                    _(f'{item.product.name}: quantity reduced to {item.product.market_quantity}')
                )
                item.quantity = item.product.market_quantity
                item.save(update_fields=['quantity'])

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
        }

    @classmethod
    @transaction.atomic
    def mark_as_checkout(cls, cart):
        """
        علامت‌گذاری سبد به عنوان در حال پرداخت

        Args:
            cart: سبد خرید
        """
        cart.status = CartStatus.CHECKOUT
        cart.save(update_fields=['status', 'updated_at'])
        logger.info(f"Cart {cart.id} marked as checkout")

    @classmethod
    @transaction.atomic
    def mark_as_ordered(cls, cart):
        """
        علامت‌گذاری سبد به عنوان سفارش داده شده

        Args:
            cart: سبد خرید
        """
        cart.status = CartStatus.ORDERED
        cart.save(update_fields=['status', 'updated_at'])
        logger.info(f"Cart {cart.id} marked as ordered")

    @classmethod
    @transaction.atomic
    def abandon_cart(cls, cart):
        """
        رها کردن سبد (منقضی شده)

        Args:
            cart: سبد خرید
        """
        cart.status = CartStatus.ABANDONED
        cart.save(update_fields=['status', 'updated_at'])
        logger.info(f"Cart {cart.id} abandoned")

    # ==================== Private Methods ====================

    @classmethod
    def _validate_product_availability(cls, product, quantity):
        """
        اعتبارسنجی موجودی محصول در مارکت

        Args:
            product: محصول
            quantity: تعداد درخواستی

        Raises:
            ValueError
        """
        if not product.is_active:
            raise ValueError(_('Product is not active.'))

        if not product.is_market_visible:
            raise ValueError(_('Product is not available in market.'))

        if product.market_status != 'published':
            raise ValueError(_('Product is not published in market.'))

        if product.market_quantity < quantity:
            raise ValueError(
                _(f'Only {product.market_quantity} available in market.')
            )

    @classmethod
    def cleanup_abandoned_carts(cls, days=30):
        """
        پاکسازی سبدهای رها شده

        Args:
            days: چند روز بعد از آخرین فعالیت

        Returns:
            int: تعداد سبدهای پاکسازی شده
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)

        count = Cart.objects.filter(
            status=CartStatus.ACTIVE,
            updated_at__lt=cutoff
        ).update(status=CartStatus.ABANDONED)

        logger.info(f"Cleaned up {count} abandoned carts older than {days} days")

        return count

    @classmethod
    def merge_carts(cls, user, session_cart_id):
        """
        ادغام سبد مهمان با سبد کاربر (بعد از لاگین)

        Args:
            user: کاربر
            session_cart_id: شناسه سبد مهمان

        Returns:
            Cart: سبد ادغام شده
        """
        try:
            session_cart = Cart.objects.get(id=session_cart_id)
            user_cart = cls.get_or_create_cart(user)

            # انتقال آیتم‌ها
            for item in session_cart.items.filter(is_active=True):
                existing = user_cart.items.filter(
                    product=item.product,
                    is_active=True
                ).first()

                if existing:
                    existing.quantity += item.quantity
                    existing.save()
                else:
                    CartItem.objects.create(
                        cart=user_cart,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                    )

            # غیرفعال کردن سبد مهمان
            session_cart.status = CartStatus.ABANDONED
            session_cart.save()

            logger.info(f"Merged session cart {session_cart_id} into user cart {user_cart.id}")

            return user_cart

        except Cart.DoesNotExist:
            return cls.get_or_create_cart(user)
