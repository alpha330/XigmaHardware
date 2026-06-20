"""
Auth Serializers
- ثبت‌نام با ایمیل
- ثبت‌نام با موبایل
- ورود
- OTP
- تغییر/بازیابی رمز عبور
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.accounts.enums import UserRole
from apps.accounts.validators import validate_iranian_phone

User = get_user_model()


class EmailRegisterSerializer(serializers.Serializer):
    """
    سریالایزر ثبت‌نام با ایمیل
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': _('Email is required.'),
            'invalid': _('Please enter a valid email address.'),
        }
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password],
        error_messages={
            'required': _('Password is required.'),
        }
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': _('Password confirmation is required.'),
        }
    )
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )
    user_type = serializers.ChoiceField(
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        required=False
    )

    def validate_email(self, value):
        """بررسی یکتایی ایمیل"""
        email = value.lower().strip()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _('This email is already registered.')
            )

        return email

    def validate_password_confirm(self, value):
        """بررسی تطابق رمز عبور"""
        data = self.get_initial()
        password = data.get('password')

        if password != value:
            raise serializers.ValidationError(
                _('Passwords do not match.')
            )

        return value

    def validate(self, data):
        """حذف password_confirm از داده‌های نهایی"""
        data.pop('password_confirm', None)
        return data


class MobileRegisterSerializer(serializers.Serializer):
    """
    سریالایزر ثبت‌نام با موبایل
    """
    mobile = serializers.CharField(
        required=True,
        max_length=11,
        validators=[validate_iranian_phone],
        error_messages={
            'required': _('Mobile number is required.'),
        }
    )
    password = serializers.CharField(
        required=False,
        write_only=True,
        style={'input_type': 'password'},
    )
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150
    )

    def validate_mobile(self, value):
        """بررسی یکتایی موبایل"""
        mobile = value.strip()

        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError(
                _('This mobile number is already registered.')
            )

        return mobile


class LoginSerializer(serializers.Serializer):
    """
    سریالایزر ورود (با ایمیل یا موبایل)
    """
    email = serializers.EmailField(
        required=False,
        error_messages={
            'invalid': _('Please enter a valid email address.'),
        }
    )
    mobile = serializers.CharField(
        required=False,
        max_length=11,
        error_messages={
            'invalid': _('Please enter a valid mobile number.'),
        }
    )
    password = serializers.CharField(
        required=False,
        write_only=True,
        style={'input_type': 'password'},
    )
    otp_code = serializers.CharField(
        required=False,
        max_length=6,
        min_length=6,
    )

    def validate(self, data):
        email = data.get('email')
        mobile = data.get('mobile')

        if not email and not mobile:
            raise serializers.ValidationError({
                'email': _('Email or mobile is required.'),
                'mobile': _('Email or mobile is required.'),
            })

        return data


class OTPSerializer(serializers.Serializer):
    """
    سریالایزر تایید OTP
    """
    mobile = serializers.CharField(
        required=True,
        max_length=11,
        validators=[validate_iranian_phone],
    )
    code = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        error_messages={
            'required': _('OTP code is required.'),
            'min_length': _('OTP code must be 6 digits.'),
            'max_length': _('OTP code must be 6 digits.'),
        }
    )
    otp_id = serializers.UUIDField(
        required=False,
        help_text=_('OTP reference ID (for verification)')
    )
    purpose = serializers.ChoiceField(
        choices=[
            ('login', _('Login')),
            ('register', _('Register')),
            ('reset_password', _('Reset Password')),
        ],
        default='login',
        required=False
    )

    def validate_code(self, value):
        """بررسی عددی بودن کد"""
        if not value.isdigit():
            raise serializers.ValidationError(
                _('OTP code must contain only digits.')
            )
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    سریالایزر تغییر رمز عبور
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': _('Current password is required.'),
        }
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password],
        error_messages={
            'required': _('New password is required.'),
        }
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': _('Password confirmation is required.'),
        }
    )

    def validate_old_password(self, value):
        """بررسی صحت رمز عبور فعلی"""
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Current password is incorrect.')
            )

        return value

    def validate(self, data):
        """بررسی تطابق رمزهای جدید"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('New passwords do not match.')
            })

        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                'new_password': _('New password must be different from current password.')
            })

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    سریالایزر درخواست بازیابی رمز عبور
    """
    email_or_mobile = serializers.CharField(
        required=True,
        error_messages={
            'required': _('Email or mobile is required.'),
        }
    )

    def validate_email_or_mobile(self, value):
        """تشخیص ایمیل یا موبایل"""
        value = value.strip()

        if '@' in value:
            # ایمیل
            from django.core.validators import validate_email
            try:
                validate_email(value)
            except Exception:
                raise serializers.ValidationError(
                    _('Invalid email address.')
                )
        else:
            # موبایل
            validate_iranian_phone(value)

        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    سریالایزر تایید بازیابی رمز عبور
    """
    email_or_mobile = serializers.CharField(
        required=True,
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
    )
    otp_id = serializers.UUIDField(
        required=False,
    )
    code = serializers.CharField(
        required=False,
        max_length=6,
    )

    def validate(self, data):
        """بررسی تطابق رمزها"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _('Passwords do not match.')
            })

        return data