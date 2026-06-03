from rest_framework import permissions
from apps.accounts.enums import UserRole
from apps.basket.enums import CartType, CartStatus


class IsCartOwner(permissions.BasePermission):
    """
    فقط صاحب سبد می‌تونه به سبد دسترسی داشته باشه

    برای Cart:
    - obj.user == request.user

    برای CartItem:
    - obj.cart.user == request.user

    برای Wishlist:
    - obj.user == request.user
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Cart
        if hasattr(obj, 'user'):
            return obj.user == user

        # CartItem
        if hasattr(obj, 'cart'):
            return obj.cart.user == user

        return False


class IsCartActive(permissions.BasePermission):
    """
    فقط سبدهای فعال قابل تغییر هستن
    """
    def has_object_permission(self, request, view, obj):
        # Cart
        if hasattr(obj, 'status'):
            return obj.status == CartStatus.ACTIVE

        # CartItem
        if hasattr(obj, 'cart'):
            return obj.cart.status == CartStatus.ACTIVE

        return False


class CanSetDiscount(permissions.BasePermission):
    """
    فقط ادمین و حسابدار می‌تونن تخفیف تنظیم کنن

    نقش‌های مجاز:
    - super_admin
    - accountant
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return (
            request.user.is_superuser or
            request.user.role in [
                UserRole.SUPER_ADMIN,
                UserRole.ACCOUNTANT,
            ]
        )


class CanManageWishlist(permissions.BasePermission):
    """
    دسترسی مدیریت Wishlist

    - ایجاد: همه کاربران
    - ویرایش/حذف: فقط صاحب Wishlist
    - تبدیل: فقط صاحب Wishlist (و اگه can_convert فعال باشه)
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # ادمین می‌تونه همه رو ببینه
        if user.is_superuser or user.role == UserRole.SUPER_ADMIN:
            return True

        # مالک
        if hasattr(obj, 'user'):
            return obj.user == user

        return False


class CanAddToCart(permissions.BasePermission):
    """
    دسترسی افزودن به سبد خرید

    شرایط:
    - کاربر احراز هویت شده
    - محصول در مارکت موجود باشه
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated


class CanCheckout(permissions.BasePermission):
    """
    دسترسی پرداخت نهایی

    شرایط:
    - فقط سبد از نوع CART
    - وضعیت ACTIVE
    - حداقل یک آیتم داشته باشه
    - تخفیف معتبر داشته باشه (اگه داره)
    """
    def has_object_permission(self, request, view, obj):
        if not obj.is_cart:
            return False

        if not obj.can_checkout:
            return False

        return True


class CanConvertWishlist(permissions.BasePermission):
    """
    دسترسی تبدیل Wishlist به Cart

    شرایط:
    - صاحب Wishlist
    - Wishlist فعال
    - can_convert = True
    - حداقل یک آیتم فعال
    - محصولات هنوز در مارکت موجود باشن
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # مالک
        if hasattr(obj, 'user') and obj.user != user:
            return False

        # فعال
        if hasattr(obj, 'is_active') and not obj.is_active:
            return False

        # قابلیت تبدیل
        if hasattr(obj, 'can_convert') and not obj.can_convert:
            return False

        # حداقل یه آیتم
        if hasattr(obj, 'cart'):
            if not obj.cart.items.filter(is_active=True).exists():
                return False

        return True


class CanUpdateCartItem(permissions.BasePermission):
    """
    دسترسی بروزرسانی آیتم سبد

    - فقط آیتم‌های فعال
    - فقط صاحب سبد
    - فقط وقتی سبد در وضعیت ACTIVE هست
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # مالک سبد
        if not obj.cart.user == user:
            return False

        # آیتم فعال
        if not obj.is_active:
            return False

        # سبد فعال
        if obj.cart.status != CartStatus.ACTIVE:
            return False

        return True


class CanViewCart(permissions.BasePermission):
    """
    دسترسی مشاهده سبد

    - صاحب سبد: همه سبدها
    - ادمین: همه سبدها
    - دیگران: فقط سبدهای عمومی (Wishlist های public)
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # ادمین همه رو می‌بینه
        if user.is_superuser or user.role == UserRole.SUPER_ADMIN:
            return True

        # صاحب سبد
        if hasattr(obj, 'user') and obj.user == user:
            return True

        # Wishlist عمومی
        if hasattr(obj, 'is_public') and obj.is_public:
            return True

        return False


class IsWishlistOwner(permissions.BasePermission):
    """
    فقط صاحب Wishlist
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsWishlistActive(permissions.BasePermission):
    """
    فقط Wishlist های فعال
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'is_active'):
            return obj.is_active
        return False


class CanViewWishlistDiscount(permissions.BasePermission):
    """
    مشاهده تخفیف Wishlist

    - صاحب Wishlist: می‌تونه ببینه
    - ادمین/مالی: می‌تونه ببینه و تنظیم کنه
    - دیگران: نمی‌تونن ببینن
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # ادمین/مالی
        if user.role in [UserRole.SUPER_ADMIN, UserRole.ACCOUNTANT] or user.is_superuser:
            return True

        # صاحب
        if hasattr(obj, 'user') and obj.user == user:
            return True

        return False


class CanClearCart(permissions.BasePermission):
    """
    دسترسی خالی کردن سبد

    - فقط صاحب سبد
    - فقط سبد فعال
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user') and obj.user != request.user:
            return False

        if hasattr(obj, 'status') and obj.status != CartStatus.ACTIVE:
            return False

        return True


class IsNotInCheckout(permissions.BasePermission):
    """
    سبد نباید در وضعیت پرداخت باشه
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'status'):
            return obj.status != CartStatus.CHECKOUT

        if hasattr(obj, 'cart'):
            return obj.cart.status != CartStatus.CHECKOUT

        return True
