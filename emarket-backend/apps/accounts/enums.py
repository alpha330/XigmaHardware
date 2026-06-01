from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """نقش‌های کاربر در سیستم"""
    SUPER_ADMIN = 'super_admin', _('Super Admin')
    CLIENT = 'client', _('Client/Customer')
    ACCOUNTANT = 'accountant', _('Accountant')
    COURIER = 'courier', _('Courier/Delivery')
    STOCK_KEEPER = 'stock_keeper', _('Stock Keeper')
    
    @classmethod
    def default(cls):
        return cls.CLIENT


class ProfileType(models.TextChoices):
    """نوع پروفایل - حقیقی یا حقوقی"""
    INDIVIDUAL = 'individual', _('Individual')
    LEGAL = 'legal', _('Legal/Company')
    
    @classmethod
    def default(cls):
        return cls.INDIVIDUAL


class VerificationType(models.TextChoices):
    """نوع احراز هویت"""
    EMAIL = 'email', _('Email')
    MOBILE = 'mobile', _('Mobile')


class OTPPurpose(models.TextChoices):
    """هدف از ارسال OTP"""
    REGISTER = 'register', _('Register')
    LOGIN = 'login', _('Login')
    RESET_PASSWORD = 'reset_password', _('Reset Password')
    CHANGE_MOBILE = 'change_mobile', _('Change Mobile')
    CHANGE_EMAIL = 'change_email', _('Change Email')
    VERIFY_PROFILE = 'verify_profile', _('Verify Profile')


class WalletTransactionType(models.TextChoices):
    """نوع تراکنش کیف پول"""
    DEPOSIT = 'deposit', _('Deposit')
    WITHDRAW = 'withdraw', _('Withdraw')
    PAYMENT = 'payment', _('Payment')
    REFUND = 'refund', _('Refund')
    COMMISSION = 'commission', _('Commission')
    BONUS = 'bonus', _('Bonus')


class WalletTransactionStatus(models.TextChoices):
    """وضعیت تراکنش کیف پول"""
    PENDING = 'pending', _('Pending')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')
    CANCELLED = 'cancelled', _('Cancelled')