"""
Profile Serializers
- نمایش پروفایل
- به‌روزرسانی پروفایل
- تغییر نوع پروفایل (حقیقی/حقوقی)
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounts.models import Profile
from apps.accounts.validators import (
    validate_national_code,
    validate_national_id,
    validate_economic_code,
    validate_postal_code,
)


class ProfileSerializer(serializers.ModelSerializer):
    """
    سریالایزر اصلی پروفایل
    """
    profile_type_display = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    missing_fields = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'profile_type', 'profile_type_display',
            'avatar', 'avatar_url', 'birth_date',
            'tel', 'address', 'postal_code',
            # Individual
            'national_code',
            # Legal
            'company_name', 'national_id', 'economic_code',
            # Status
            'is_completed', 'completion_percentage', 'missing_fields',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_completed',
            'created_at', 'updated_at',
        ]

    def get_profile_type_display(self, obj):
        """نمایش نوع پروفایل"""
        if obj.is_individual:
            return {
                'code': 'individual',
                'label': _('Individual'),
                'icon': '👤',
            }
        return {
            'code': 'legal',
            'label': _('Legal/Company'),
            'icon': '🏢',
        }

    def get_avatar_url(self, obj):
        """URL آواتار"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def get_completion_percentage(self, obj):
        """درصد تکمیل"""
        from apps.accounts.services.profile_service import ProfileService
        return ProfileService.calculate_completion_percentage(obj)

    def get_missing_fields(self, obj):
        """فیلدهای تکمیل نشده"""
        from apps.accounts.services.profile_service import ProfileService
        return ProfileService.get_missing_fields(obj)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    سریالایزر به‌روزرسانی پروفایل
    """

    class Meta:
        model = Profile
        fields = [
            'avatar', 'birth_date',
            'tel', 'address', 'postal_code',
            'national_code', 'company_name', 'national_id', 'economic_code'
        ]

    def validate_postal_code(self, value):
        """اعتبارسنجی کد پستی"""
        if value:
            validate_postal_code(value)
        return value

    def validate_avatar(self, value):
        """اعتبارسنجی آواتار"""
        if value:
            # محدودیت حجم (5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    _('Avatar size must be less than 5MB.')
                )

            # محدودیت فرمت
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    _('Avatar must be JPEG, PNG, or WebP format.')
                )

        return value


class ProfileSwitchToLegalSerializer(serializers.Serializer):
    """
    سریالایزر تغییر پروفایل به حقوقی
    """
    company_name = serializers.CharField(
        required=True,
        max_length=200,
        min_length=2,
        error_messages={
            'required': _('Company name is required.'),
        }
    )
    national_id = serializers.CharField(
        required=True,
        max_length=11,
        min_length=11,
        error_messages={
            'required': _('National ID is required.'),
        }
    )
    economic_code = serializers.CharField(
        required=True,
        max_length=12,
        min_length=12,
        error_messages={
            'required': _('Economic code is required.'),
        }
    )

    def validate_national_id(self, value):
        """اعتبارسنجی شناسه ملی"""
        validate_national_id(value)

        # بررسی یکتایی
        if Profile.objects.filter(national_id=value).exists():
            raise serializers.ValidationError(
                _('This national ID is already registered.')
            )

        return value

    def validate_economic_code(self, value):
        """اعتبارسنجی کد اقتصادی"""
        validate_economic_code(value)

        # بررسی یکتایی
        if Profile.objects.filter(economic_code=value).exists():
            raise serializers.ValidationError(
                _('This economic code is already registered.')
            )

        return value


class ProfileSwitchToIndividualSerializer(serializers.Serializer):
    """
    سریالایزر تغییر پروفایل به حقیقی
    """
    national_code = serializers.CharField(
        required=True,
        max_length=10,
        min_length=10,
        error_messages={
            'required': _('National code is required.'),
        }
    )

    def validate_national_code(self, value):
        """اعتبارسنجی کد ملی"""
        validate_national_code(value)

        # بررسی یکتایی
        if Profile.objects.filter(national_code=value).exists():
            raise serializers.ValidationError(
                _('This national code is already registered.')
            )

        return value


class ProfileCompletionSerializer(serializers.Serializer):
    """
    سریالایزر بررسی تکمیل پروفایل
    """
    # فقط خواندنی - برای نمایش وضعیت تکمیل
    pass