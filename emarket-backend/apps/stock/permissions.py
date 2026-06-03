
from rest_framework import permissions
from apps.accounts.enums import UserRole


class CanManageWarehouse(permissions.BasePermission):
    """
    فقط super_admin و stock_keeper می‌تونن انبار مدیریت کنن
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [
            UserRole.SUPER_ADMIN,
            UserRole.STOCK_KEEPER,
        ] or request.user.is_superuser


class IsWarehouseStaff(permissions.BasePermission):
    """
    کارکنان انبار (مدیر و staff)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [
            UserRole.SUPER_ADMIN,
            UserRole.STOCK_KEEPER,
        ] or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.role == UserRole.SUPER_ADMIN:
            return True

        # چک می‌کنه کاربر به این انبار دسترسی داره یا نه
        if hasattr(obj, 'warehouse'):
            warehouse = obj.warehouse
        elif hasattr(obj, 'inventory_item'):
            warehouse = obj.inventory_item.warehouse
        else:
            return False

        return (
            warehouse.manager == user or
            warehouse.staff.filter(id=user.id).exists()
        )


class CanManageStock(permissions.BasePermission):
    """
    مدیریت محصولات و موجودی
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [
            UserRole.SUPER_ADMIN,
            UserRole.STOCK_KEEPER,
        ] or request.user.is_superuser


class CanManageMarket(permissions.BasePermission):
    """
    مدیریت انتشار در مارکت
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [
            UserRole.SUPER_ADMIN,
            UserRole.STOCK_KEEPER,
            UserRole.ACCOUNTANT,
        ] or request.user.is_superuser