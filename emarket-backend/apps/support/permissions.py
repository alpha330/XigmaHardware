from rest_framework import permissions
from apps.accounts.enums import UserRole


class CanManageSupport(permissions.BasePermission):
    """ادمین و حسابدار می‌تونن تیکت مدیریت کنن"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role in [UserRole.SUPER_ADMIN, UserRole.ACCOUNTANT]
        )