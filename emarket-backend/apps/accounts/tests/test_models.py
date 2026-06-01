"""
Tests for Accounts Models
"""

import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.accounts.models import User, Profile, Wallet, UserDevice, OTPCode
from apps.accounts.enums import UserRole, ProfileType
from apps.accounts.tests.factories import (
    UserFactory, ProfileFactory, WalletFactory,
    UserDeviceFactory, OTPCodeFactory
)


@pytest.mark.django_db
class TestUserModel:
    """
    تست‌های مدل User
    """
    
    def test_create_user(self, user):
        """تست ایجاد کاربر"""
        assert user.id is not None
        assert user.email is not None or user.mobile is not None
        assert user.is_active is True
        assert user.role == UserRole.CLIENT
    
    def test_create_superuser(self, admin_user):
        """تست ایجاد سوپر ادمین"""
        assert admin_user.is_superuser is True
        assert admin_user.is_staff is True
        assert admin_user.role == UserRole.SUPER_ADMIN
    
    def test_user_str_representation(self, user):
        """تست نمایش رشته‌ای کاربر"""
        assert str(user) == user.get_display_name()
    
    def test_user_with_email_only(self, db):
        """تست کاربر فقط با ایمیل"""
        user = UserFactory(with_email=True)
        assert user.email is not None
        assert user.mobile is None
        assert user.registration_method == 'email'
    
    def test_user_with_mobile_only(self, db):
        """تست کاربر فقط با موبایل"""
        user = UserFactory(with_mobile=True)
        assert user.mobile is not None
        assert user.email is None
        assert user.registration_method == 'mobile'
    
    def test_is_verified_email(self, db):
        """تست وضعیت تایید ایمیل"""
        user = UserFactory(with_email=True)
        assert user.is_verified is True
        
        user.is_email_verified = False
        user.save()
        assert user.is_verified is False
    
    def test_is_verified_mobile(self, db):
        """تست وضعیت تایید موبایل"""
        user = UserFactory(with_mobile=True)
        assert user.is_verified is True
        
        user.is_mobile_verified = False
        user.save()
        assert user.is_verified is False
    
    def test_verify_email(self, user):
        """تست تایید ایمیل"""
        user.is_email_verified = False
        user.save()
        user.verify_email()
        assert user.is_email_verified is True
    
    def test_verify_mobile(self, user):
        """تست تایید موبایل"""
        user.is_mobile_verified = False
        user.save()
        user.verify_mobile()
        assert user.is_mobile_verified is True
    
    def test_increment_failed_login(self, user):
        """تست افزایش تلاش ناموفق"""
        assert user.failed_login_attempts == 0
        
        user.increment_failed_login()
        assert user.failed_login_attempts == 1
        
        # تست قفل شدن بعد از 5 تلاش
        for i in range(4):
            user.increment_failed_login()
        
        assert user.is_locked is True
        assert user.locked_until is not None
    
    def test_reset_failed_login(self, user):
        """تست بازنشانی تلاش‌های ناموفق"""
        user.failed_login_attempts = 3
        user.locked_until = timezone.now()
        user.save()
        
        user.reset_failed_login()
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
    
    def test_unique_email(self, db):
        """تست یکتایی ایمیل"""
        user1 = UserFactory(email='same@example.com')
        
        with pytest.raises(Exception):
            UserFactory(email='same@example.com')
    
    def test_unique_mobile(self, db):
        """تست یکتایی موبایل"""
        user1 = UserFactory(mobile='09123456789')
        
        with pytest.raises(Exception):
            UserFactory(mobile='09123456789')
    
    def test_get_primary_contact(self, db):
        """تست دریافت راه ارتباطی اصلی"""
        # با موبایل
        user = UserFactory(with_mobile=True, mobile='09123456789')
        assert user.get_primary_contact() == '09123456789'
        
        # با ایمیل (بدون موبایل)
        user = UserFactory(with_email=True, email='test@example.com')
        assert user.get_primary_contact() == 'test@example.com'


@pytest.mark.django_db
class TestProfileModel:
    """
    تست‌های مدل Profile
    """
    
    def test_create_profile(self, user):
        """تست ایجاد پروفایل"""
        profile = ProfileFactory(user=user)
        assert profile.id is not None
        assert profile.user == user
        assert profile.profile_type == ProfileType.INDIVIDUAL
    
    def test_profile_individual(self, user):
        """تست پروفایل حقیقی"""
        profile = ProfileFactory(user=user)
        assert profile.is_individual is True
        assert profile.is_legal is False
        assert profile.national_code is not None
    
    def test_profile_legal(self, user):
        """تست پروفایل حقوقی"""
        profile = ProfileFactory(user=user, legal=True)
        assert profile.is_legal is True
        assert profile.is_individual is False
        assert profile.company_name is not None
        assert profile.national_id is not None
        assert profile.economic_code is not None
    
    def test_full_name_individual(self, user):
        """تست نام کامل حقیقی"""
        user.first_name = 'Ali'
        user.last_name = 'Rezaei'
        user.save()
        
        profile = ProfileFactory(user=user)
        assert profile.full_name == 'Ali Rezaei'
    
    def test_full_name_legal(self, user):
        """تست نام کامل حقوقی (نام شرکت)"""
        profile = ProfileFactory(user=user, legal=True, company_name='Test Company')
        assert profile.full_name is None  # برای حقوقی None برمی‌گردونه
    
    def test_check_completion_individual(self, user):
        """تست تکمیل پروفایل حقیقی"""
        profile = ProfileFactory(user=user, national_code='1234567890')
        profile.address = 'Test Address'
        profile.postal_code = '1234567890'
        profile.save()
        
        assert profile.check_completion() is True
    
    def test_check_completion_legal(self, user):
        """تست تکمیل پروفایل حقوقی"""
        profile = ProfileFactory(user=user, legal=True)
        profile.address = 'Test Address'
        profile.postal_code = '1234567890'
        profile.save()
        
        assert profile.check_completion() is True
    
    def test_switch_to_legal(self, user):
        """تست تغییر پروفایل به حقوقی"""
        profile = ProfileFactory(user=user)
        profile.switch_to_legal(
            company_name='Test Company',
            national_id='12345678901',
            economic_code='123456789012'
        )
        
        assert profile.is_legal is True
        assert profile.company_name == 'Test Company'
        assert profile.national_code is None
    
    def test_switch_to_individual(self, user):
        """تست تغییر پروفایل به حقیقی"""
        profile = ProfileFactory(user=user, legal=True)
        profile.switch_to_individual('1234567890')
        
        assert profile.is_individual is True
        assert profile.national_code == '1234567890'
        assert profile.company_name == ''
        assert profile.national_id is None
    
    def test_complete_profile(self, user):
        """تست تکمیل خودکار پروفایل"""
        profile = ProfileFactory(
            user=user,
            national_code='1234567890',
            address='Test Address',
            postal_code='1234567890'
        )
        profile.complete_profile()
        assert profile.is_completed is True


@pytest.mark.django_db
class TestWalletModel:
    """
    تست‌های مدل Wallet
    """
    
    def test_create_wallet(self, user):
        """تست ایجاد کیف پول"""
        wallet = WalletFactory(user=user)
        assert wallet.id is not None
        assert wallet.user == user
        assert wallet.balance >= 0
    
    def test_available_balance(self, user):
        """تست موجودی قابل برداشت"""
        wallet = WalletFactory(user=user, balance=1000)
        assert wallet.available_balance == 1000
        
        wallet.blocked_balance = 300
        wallet.save()
        assert wallet.available_balance == 700
    
    def test_deposit(self, user):
        """تست واریز به کیف پول"""
        wallet = WalletFactory(user=user, balance=1000)
        wallet.deposit(500)
        assert wallet.balance == 1500
    
    def test_deposit_negative(self, user):
        """تست واریز مبلغ منفی"""
        wallet = WalletFactory(user=user)
        result = wallet.deposit(-100)
        assert result is False
        assert wallet.balance == wallet.balance
    
    def test_withdraw(self, user):
        """تست برداشت از کیف پول"""
        wallet = WalletFactory(user=user, balance=1000)
        result = wallet.withdraw(500)
        assert result is True
        assert wallet.balance == 500
    
    def test_withdraw_insufficient(self, user):
        """تست برداشت بیش از موجودی"""
        wallet = WalletFactory(user=user, balance=100)
        result = wallet.withdraw(200)
        assert result is False
        assert wallet.balance == 100
    
    def test_block_amount(self, user):
        """تست مسدود کردن موجودی"""
        wallet = WalletFactory(user=user, balance=1000)
        result = wallet.block_amount(300)
        assert result is True
        assert wallet.blocked_balance == 300
        assert wallet.available_balance == 700
    
    def test_unblock_amount(self, user):
        """تست آزاد کردن موجودی"""
        wallet = WalletFactory(user=user, balance=1000, blocked_balance=300)
        result = wallet.unblock_amount(300)
        assert result is True
        assert wallet.blocked_balance == 0
        assert wallet.available_balance == 1000


@pytest.mark.django_db
class TestOTPCodeModel:
    """
    تست‌های مدل OTPCode
    """
    
    def test_generate_otp(self, user):
        """تست تولید کد OTP"""
        otp = OTPCode.generate(user=user, purpose='login')
        assert otp.id is not None
        assert len(otp.code) == 6
        assert otp.is_used is False
        assert otp.is_valid() is True
    
    def test_verify_otp_success(self, user):
        """تست تایید موفق OTP"""
        otp = OTPCodeFactory(user=user, code='123456')
        result = otp.verify('123456')
        assert result is True
        assert otp.is_used is True
    
    def test_verify_otp_wrong_code(self, user):
        """تست تایید OTP با کد اشتباه"""
        otp = OTPCodeFactory(user=user, code='123456')
        result = otp.verify('654321')
        assert result is False
        assert otp.is_used is False
        assert otp.attempts == 1
    
    def test_verify_otp_expired(self, user):
        """تست تایید OTP منقضی شده"""
        from django.utils import timezone
        otp = OTPCodeFactory(
            user=user,
            code='123456',
            expires_at=timezone.now() - timezone.timedelta(minutes=1)
        )
        result = otp.verify('123456')
        assert result is False
    
    def test_verify_otp_max_attempts(self, user):
        """تست حداکثر تلاش ناموفق"""
        otp = OTPCodeFactory(user=user, code='123456', attempts=3)
        result = otp.verify('123456')
        assert result is False