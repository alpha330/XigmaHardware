"""
User Serializers
- نمایش اطلاعات کاربر
- به‌روزرسانی کاربر
- تغییر نقش
"""

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounts.enums import UserRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    سریالایزر اصلی کاربر (نمایش کامل)
    """
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    is_verified = serializers.BooleanField(read_only=True)
    wallet_balance = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'mobile', 'first_name', 'last_name',
            'full_name', 'user_type', 'role',
            'avatar_url', 'is_email_verified', 'is_mobile_verified',
            'is_verified', 'is_active', 'is_staff',
            'wallet_balance', 'profile_completion',
            'registration_method', 'last_login_method',
            'date_joined', 'last_login', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'email', 'mobile', 'is_email_verified',
            'is_mobile_verified', 'is_active', 'is_staff',
            'registration_method', 'date_joined',
            'last_login', 'created_at', 'updated_at',
        ]
    
    def get_full_name(self, obj):
        """نام کامل کاربر"""
        if hasattr(obj, 'profile'):
            if obj.profile.is_legal and obj.profile.company_name:
                return obj.profile.company_name
            elif obj.first_name or obj.last_name:
                return f"{obj.first_name} {obj.last_name}".strip()
        return obj.email or obj.mobile or str(obj.id)
    
    def get_avatar_url(self, obj):
        """URL آواتار"""
        if hasattr(obj, 'profile') and obj.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.avatar.url)
            return obj.profile.avatar.url
        return None
    
    def get_wallet_balance(self, obj):
        """موجودی کیف پول"""
        if hasattr(obj, 'wallet'):
            return {
                'balance': float(obj.wallet.balance),
                'available': float(obj.wallet.available_balance),
                'blocked': float(obj.wallet.blocked_balance),
            }
        return None
    
    def get_profile_completion(self, obj):
        """درصد تکمیل پروفایل"""
        if hasattr(obj, 'profile'):
            from apps.accounts.services.profile_service import ProfileService
            return ProfileService.calculate_completion_percentage(obj.profile)
        return 0


class UserListSerializer(serializers.ModelSerializer):
    """
    سریالایزر لیست کاربران (خلاصه - برای ادمین)
    """
    full_name = serializers.SerializerMethodField()
    profile_type = serializers.SerializerMethodField()
    is_verified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'mobile', 'full_name',
            'role', 'profile_type',
            'is_active', 'is_verified',
            'date_joined', 'last_login',
        ]
    
    def get_full_name(self, obj):
        if hasattr(obj, 'profile'):
            if obj.profile.is_legal and obj.profile.company_name:
                return obj.profile.company_name
            elif obj.first_name or obj.last_name:
                return f"{obj.first_name} {obj.last_name}".strip()
        return obj.email or obj.mobile or '-'
    
    def get_profile_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.profile_type
        return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    سریالایزر به‌روزرسانی کاربر
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name',
        ]
    
    def validate_first_name(self, value):
        """اعتبارسنجی نام"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                _('First name must be at least 2 characters.')
            )
        return value.strip() if value else value
    
    def validate_last_name(self, value):
        """اعتبارسنجی نام خانوادگی"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                _('Last name must be at least 2 characters.')
            )
        return value.strip() if value else value


class UserRoleChangeSerializer(serializers.Serializer):
    """
    سریالایزر تغییر نقش کاربر (فقط ادمین)
    """
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        required=True,
        error_messages={
            'required': _('Role is required.'),
            'invalid_choice': _('Invalid role selected.'),
        }
    )
    
    def validate_role(self, value):
        """بررسی منطق تغییر نقش"""
        user = self.context.get('user')
        
        if user and user.role == value:
            raise serializers.ValidationError(
                _('User already has this role.')
            )
        
        # فقط سوپر ادمین می‌تواند نقش super_admin را بدهد
        if value == UserRole.SUPER_ADMIN:
            request = self.context.get('request')
            if request and not request.user.is_superuser:
                raise serializers.ValidationError(
                    _('Only super admins can assign super admin role.')
                )
        
        return value


class UserDeactivateSerializer(serializers.Serializer):
    """
    سریالایزر غیرفعال‌سازی حساب
    """
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': _('Password is required to deactivate account.'),
        }
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )