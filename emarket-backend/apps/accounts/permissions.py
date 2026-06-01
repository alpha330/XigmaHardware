from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from apps.accounts.enums import UserRole


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    اجازه ویرایش فقط برای صاحب پروفایل
    """
    
    def has_object_permission(self, request, view, obj):
        # اجازه خواندن برای همه کاربران احراز هویت شده
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # فقط صاحب شیء می‌تواند ویرایش کند
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """
    فقط صاحب شیء دسترسی دارد
    """
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    فقط صاحب شیء یا ادمین دسترسی دارد
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        # بررسی اینکه شیء user دارد یا خودش user است
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsSuperAdmin(permissions.BasePermission):
    """
    فقط سوپر ادمین دسترسی دارد
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_superuser
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrStaff(permissions.BasePermission):
    """
    فقط ادمین‌ها و کارمندان دسترسی دارند
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.is_staff)
        )


class HasRole(permissions.BasePermission):
    """
    دسترسی بر اساس نقش کاربر
    """
    
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles if isinstance(allowed_roles, list) else [allowed_roles]
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in self.allowed_roles
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsClient(permissions.BasePermission):
    """
    فقط کاربران با نقش مشتری
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == UserRole.CLIENT
        )


class IsAccountant(permissions.BasePermission):
    """
    فقط حسابدارها
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == UserRole.ACCOUNTANT
        )


class IsCourier(permissions.BasePermission):
    """
    فقط پیک‌ها
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == UserRole.COURIER
        )


class IsStockKeeper(permissions.BasePermission):
    """
    فقط انباردارها
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == UserRole.STOCK_KEEPER
        )


class IsVerified(permissions.BasePermission):
    """
    فقط کاربران تایید شده
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsProfileCompleted(permissions.BasePermission):
    """
    فقط کاربرانی که پروفایلشان تکمیل است
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        return request.user.profile.is_completed


class IsWalletActive(permissions.BasePermission):
    """
    فقط کاربرانی که کیف پول فعال دارند
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'wallet'):
            return False
        
        return request.user.wallet.is_active


class CanManageWallet(permissions.BasePermission):
    """
    اجازه مدیریت کیف پول (فقط صاحب کیف پول)
    """
    
    def has_object_permission(self, request, view, obj):
        # برای مدل Wallet
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # برای مدل WalletTransaction
        if hasattr(obj, 'wallet'):
            return obj.wallet.user == request.user
        
        return False


class ReadOnly(permissions.BasePermission):
    """
    فقط دسترسی خواندنی
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrReadOnlyForProfile(permissions.BasePermission):
    """
    دسترسی کامل برای صاحب پروفایل، فقط خواندنی برای دیگران
    """
    
    def has_object_permission(self, request, view, obj):
        # همه می‌توانند پروفایل‌های عمومی را ببینند
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # فقط صاحب پروفایل می‌تواند ویرایش کند
        return obj.user == request.user


class IsDeviceOwner(permissions.BasePermission):
    """
    فقط صاحب دستگاه می‌تواند آن را مدیریت کند
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user