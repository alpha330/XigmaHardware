from rest_framework import permissions
from apps.accounts.enums import UserRole


class CanManageGateway(permissions.BasePermission):
    """
    فقط ادمین می‌تونه درگاه‌ها رو مدیریت کنه
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser or
            request.user.role == UserRole.SUPER_ADMIN
        )