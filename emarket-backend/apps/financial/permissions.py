from rest_framework import permissions
from apps.accounts.enums import UserRole


class CanManageFinancial(permissions.BasePermission):
    """
    دسترسی مدیریت مالی

    نقش‌های مجاز:
    - super_admin
    - accountant
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser or
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.ACCOUNTANT]
        )


class CanViewOwnInvoices(permissions.BasePermission):
    """
    کاربران عادی فقط فاکتورهای خودشون رو ببینن
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser or user.role in [UserRole.SUPER_ADMIN, UserRole.ACCOUNTANT]:
            return True

        if hasattr(obj, 'user') and obj.user == user:
            return True

        return False


class CanVerifyPayment(permissions.BasePermission):
    """
    فقط ادمین و حسابدار می‌تونن پرداخت رو تایید کنن
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser or
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.ACCOUNTANT]
        )