from rest_framework import permissions
from apps.accounts.enums import UserRole


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    دسترسی نوشتن فقط برای ادمین، بقیه فقط خواندنی

    استفاده برای: Page, Article, News
    """
    def has_permission(self, request, view):
        # همه می‌تونن بخونن
        if request.method in permissions.SAFE_METHODS:
            return True

        # فقط ادمین می‌تونه بنویسه
        return request.user.is_authenticated and (
            request.user.is_superuser or
            request.user.role == UserRole.SUPER_ADMIN
        )


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    نویسنده یا ادمین می‌تونن ویرایش کنن

    استفاده برای: Article (نویسنده خودش)
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        # ادمین
        if request.user.is_superuser or request.user.role == UserRole.SUPER_ADMIN:
            return True

        # نویسنده
        if hasattr(obj, 'author') and obj.author == request.user:
            return True

        return False


class IsAdminOnly(permissions.BasePermission):
    """
    فقط ادمین دسترسی کامل داره

    استفاده برای: ContactMessage (مشاهده)، Newsletter (مدیریت)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.is_superuser or request.user.role == UserRole.SUPER_ADMIN


class AllowCreateOnly(permissions.BasePermission):
    """
    همه می‌تونن ایجاد کنن (POST)، بقیه عملیات فقط ادمین

    استفاده برای: ContactMessage (ایجاد توسط همه)
    """
    def has_permission(self, request, view):
        # همه می‌تونن POST کنن (ارسال پیام)
        if request.method == 'POST':
            return True

        # بقیه عملیات فقط ادمین
        if not request.user.is_authenticated:
            return False

        return request.user.is_superuser or request.user.role == UserRole.SUPER_ADMIN


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    صاحب یا ادمین

    استفاده برای: Newsletter (کاربر خودش unsubscribe کنه)
    """
    def has_permission(self, request, view):
        # Subscribe رو همه می‌تونن
        if view.action == 'subscribe':
            return True

        # بقیه فقط ادمین
        if not request.user.is_authenticated:
            return False

        return request.user.is_superuser or request.user.role == UserRole.SUPER_ADMIN


class PublishedOnly(permissions.BasePermission):
    """
    فقط محتوای منتشر شده قابل مشاهده است (برای کاربران عادی)
    ادمین همه رو می‌بینه

    استفاده برای: Article, News
    """
    def has_permission(self, request, view):
        # ادمین همه رو می‌بینه
        if request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == UserRole.SUPER_ADMIN
        ):
            return True

        # کاربران عادی فقط published
        return True  # فیلتر توی queryset انجام میشه