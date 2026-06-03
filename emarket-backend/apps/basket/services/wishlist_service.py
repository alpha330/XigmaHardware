import logging
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.basket.models import Wishlist, Cart
from apps.basket.enums import CartType, CartStatus

logger = logging.getLogger(__name__)


class WishlistService:
    """
    سرویس مدیریت سبد آرزوها

    عملیات‌های اصلی:
    - ایجاد Wishlist
    - افزودن/حذف محصول
    - تبدیل به Cart
    - کپی کردن
    - مدیریت بودجه
    - اشتراک‌گذاری
    """

    @classmethod
    @transaction.atomic
    def create_wishlist(cls, user, name, description='', budget_limit=None, target_date=None):
        """
        ایجاد Wishlist جدید

        Args:
            user: کاربر
            name: نام
            description: توضیحات
            budget_limit: سقف بودجه
            target_date: تاریخ هدف خرید

        Returns:
            Wishlist
        """
        # چک نکنیم اسم تکراری هست یا نه
        if Wishlist.objects.filter(user=user, name=name, is_active=True).exists():
            raise ValueError(_('You already have a wishlist with this name.'))

        wishlist = Wishlist.objects.create(
            user=user,
            name=name,
            description=description,
            budget_limit=budget_limit,
            target_date=target_date,
        )

        # ایجاد Cart متصل
        Cart.objects.create(
            user=user,
            cart_type=CartType.WISHLIST,
            status=CartStatus.ACTIVE,
            name=name,
            converted_from_wishlist=wishlist,
        )

        logger.info(f"Wishlist created: {name} for user {user.email or user.mobile}")

        return wishlist

    @classmethod
    @transaction.atomic
    def update_wishlist(cls, wishlist, data):
        """
        بروزرسانی Wishlist

        Args:
            wishlist: Wishlist
            data: دیکشنری داده‌های جدید

        Returns:
            Wishlist
        """
        allowed_fields = [
            'name', 'description', 'budget_limit',
            'target_date', 'is_public',
        ]

        for field in allowed_fields:
            if field in data:
                setattr(wishlist, field, data[field])

        wishlist.save()

        # آپدیت نام Cart متصل
        if hasattr(wishlist, 'cart') and 'name' in data:
            wishlist.cart.name = data['name']
            wishlist.cart.save(update_fields=['name'])

        logger.info(f"Wishlist updated: {wishlist.id}")

        return wishlist

    @classmethod
    @transaction.atomic
    def delete_wishlist(cls, wishlist):
        """
        حذف (غیرفعال‌سازی) Wishlist

        Args:
            wishlist: Wishlist
        """
        wishlist.is_active = False
        wishlist.save(update_fields=['is_active', 'updated_at'])

        # غیرفعال کردن Cart متصل
        if hasattr(wishlist, 'cart'):
            wishlist.cart.status = CartStatus.ABANDONED
            wishlist.cart.save(update_fields=['status'])

        logger.info(f"Wishlist deleted: {wishlist.id}")

    @classmethod
    @transaction.atomic
    def duplicate_wishlist(cls, wishlist):
        """
        کپی کردن Wishlist با همه آیتم‌ها

        Args:
            wishlist: Wishlist اصلی

        Returns:
            Wishlist: کپی شده
        """
        new_wishlist = Wishlist.objects.create(
            user=wishlist.user,
            name=f"{wishlist.name} (Copy)",
            description=wishlist.description,
            budget_limit=wishlist.budget_limit,
            target_date=wishlist.target_date,
        )

        # کپی آیتم‌ها
        if hasattr(wishlist, 'cart'):
            new_cart = Cart.objects.create(
                user=wishlist.user,
                cart_type=CartType.WISHLIST,
                status=CartStatus.ACTIVE,
                name=new_wishlist.name,
                converted_from_wishlist=new_wishlist,
            )

            for item in wishlist.cart.items.filter(is_active=True):
                from apps.basket.models import CartItem
                CartItem.objects.create(
                    cart=new_cart,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    notes=item.notes,
                )

        logger.info(f"Wishlist duplicated: {wishlist.id} -> {new_wishlist.id}")

        return new_wishlist

    @classmethod
    @transaction.atomic
    def convert_to_cart(cls, wishlist):
        """
        تبدیل Wishlist به سبد خرید واقعی

        Args:
            wishlist: Wishlist

        Returns:
            Cart: سبد خرید
        """
        if not wishlist.is_active:
            raise ValueError(_('Wishlist is not active.'))

        if not wishlist.can_convert:
            raise ValueError(_('Conversion is blocked by admin.'))

        if not hasattr(wishlist, 'cart'):
            raise ValueError(_('Wishlist has no items.'))

        from apps.basket.services.cart_service import CartService
        cart = CartService.convert_wishlist_to_cart(wishlist.cart)

        # آپدیت آمار Wishlist
        wishlist.conversion_count += 1
        wishlist.converted_at = timezone.now()
        wishlist.save(update_fields=['conversion_count', 'converted_at', 'updated_at'])

        logger.info(f"Wishlist {wishlist.id} converted to Cart {cart.id}")

        return cart

    @classmethod
    def get_budget_analysis(cls, wishlist):
        """
        تحلیل بودجه Wishlist

        Args:
            wishlist: Wishlist

        Returns:
            dict
        """
        if not wishlist.budget_limit:
            return {'has_budget': False}

        total = wishlist.estimated_total if hasattr(wishlist, 'cart') else 0

        return {
            'has_budget': True,
            'budget_limit': float(wishlist.budget_limit),
            'estimated_total': float(total),
            'remaining': float(max(0, wishlist.budget_limit - total)),
            'is_over_budget': total > wishlist.budget_limit,
            'overspent_by': float(max(0, total - wishlist.budget_limit)),
            'utilization_percent': round(float(total / wishlist.budget_limit * 100), 1) if wishlist.budget_limit > 0 else 0,
        }

    @classmethod
    def get_user_wishlists_summary(cls, user):
        """
        خلاصه Wishlist های کاربر

        Args:
            user: کاربر

        Returns:
            dict
        """
        wishlists = Wishlist.objects.filter(user=user, is_active=True)

        total_value = 0
        for w in wishlists:
            if hasattr(w, 'cart'):
                total_value += w.cart.grand_total

        return {
            'total_wishlists': wishlists.count(),
            'active_wishlists': wishlists.filter(is_active=True).count(),
            'total_estimated_value': float(total_value),
            'with_budget': wishlists.filter(budget_limit__isnull=False).count(),
            'with_discount': sum(
                1 for w in wishlists
                if hasattr(w, 'cart') and (w.cart.discount_percent > 0 or w.cart.discount_amount > 0)
            ),
            'recently_converted': wishlists.filter(
                converted_at__isnull=False
            ).order_by('-converted_at')[:5].values('id', 'name', 'converted_at'),
        }

    @classmethod
    @transaction.atomic
    def toggle_conversion(cls, wishlist, allow=True, admin_user=None):
        """
        فعال/غیرفعال کردن قابلیت تبدیل (توسط ادمین)

        Args:
            wishlist: Wishlist
            allow: فعال یا غیرفعال
            admin_user: ادمین
        """
        wishlist.can_convert = allow
        wishlist.save(update_fields=['can_convert', 'updated_at'])

        action = 'enabled' if allow else 'disabled'
        logger.info(
            f"Wishlist {wishlist.id} conversion {action} "
            f"by {admin_user.get_display_name() if admin_user else 'system'}"
        )

    @classmethod
    def cleanup_old_wishlists(cls, days=180):
        """
        پاکسازی Wishlist های قدیمی و غیرفعال

        Args:
            days: چند روز

        Returns:
            int: تعداد پاکسازی شده
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)

        count = Wishlist.objects.filter(
            is_active=False,
            updated_at__lt=cutoff
        ).delete()[0]

        logger.info(f"Cleaned up {count} old wishlists")

        return count
