from rest_framework import permissions
from apps.accounts.enums import UserRole


class CanManageLogistics(permissions.BasePermission):
    """
    دسترسی مدیریت لجستیک

    نقش‌های مجاز:
    - super_admin
    - stock_keeper (انباردار)
    - courier (خود پیک)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser or
            request.user.role in [
                UserRole.SUPER_ADMIN,
                UserRole.STOCK_KEEPER,
                UserRole.COURIER,
            ]
        )


class IsCourierOwner(permissions.BasePermission):
    """فقط خود پیک"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsAddressOwner(permissions.BasePermission):
    """فقط صاحب آدرس"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user