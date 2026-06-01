"""
Tests for Services
"""

import pytest
from apps.accounts.services.auth_service import AuthService
from apps.accounts.services.user_service import UserService
from apps.accounts.services.profile_service import ProfileService
from apps.accounts.services.wallet_service import WalletService
from apps.accounts.tests.factories import UserFactory, ProfileFactory, WalletFactory


@pytest.mark.django_db
class TestAuthService:
    """
    تست‌های AuthService
    """
    
    def test_register_by_email(self):
        """تست ثبت‌نام با ایمیل"""
        user = AuthService.register_by_email(
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        
        assert user.email == 'test@example.com'
        assert user.registration_method == 'email'
    
    def test_register_by_mobile(self):
        """تست ثبت‌نام با موبایل"""
        user = AuthService.register_by_mobile(
            mobile='09123456789',
            password='TestPass123!'
        )
        
        assert user.mobile == '09123456789'
        assert user.registration_method == 'mobile'
    
    def test_authenticate_with_email(self, test_password):
        """تست احراز هویت با ایمیل"""
        user = UserFactory(email='test@example.com')
        user.set_password(test_password)
        user.save()
        
        auth_user = AuthService.authenticate_user(
            email='test@example.com',
            password=test_password
        )
        
        assert auth_user is not None
        assert auth_user.email == 'test@example.com'
    
    def test_authenticate_invalid(self):
        """تست احراز هویت ناموفق"""
        auth_user = AuthService.authenticate_user(
            email='nonexistent@example.com',
            password='WrongPass123!'
        )
        
        assert auth_user is None
    
    def test_find_user_by_email(self, user):
        """تست پیدا کردن کاربر با ایمیل"""
        found = AuthService.find_user_by_email_or_mobile(user.email)
        assert found == user
    
    def test_find_user_by_mobile(self):
        """تست پیدا کردن کاربر با موبایل"""
        user = UserFactory(mobile='09123456789')
        found = AuthService.find_user_by_email_or_mobile('09123456789')
        assert found == user
    
    def test_generate_and_verify_email_token(self, user):
        """تست تولید و تایید توکن ایمیل"""
        token = AuthService.generate_email_token(user)
        verified_user = AuthService.verify_email_token(token)
        assert verified_user == user


@pytest.mark.django_db
class TestUserService:
    """
    تست‌های UserService
    """
    
    def test_update_user(self, user):
        """تست به‌روزرسانی کاربر"""
        updated = UserService.update_user(user, {
            'first_name': 'Updated',
            'last_name': 'Name'
        })
        
        assert updated.first_name == 'Updated'
        assert updated.last_name == 'Name'
    
    def test_deactivate_user(self, user):
        """تست غیرفعال‌سازی کاربر"""
        result = UserService.deactivate_user(user, 'Test reason')
        user.refresh_from_db()
        
        assert result is True
        assert user.is_active is False
    
    def test_activate_user(self, user):
        """تست فعال‌سازی مجدد کاربر"""
        user.is_active = False
        user.save()
        
        result = UserService.activate_user(user)
        user.refresh_from_db()
        
        assert result is True
        assert user.is_active is True
    
    def test_change_role(self, user):
        """تست تغییر نقش"""
        updated = UserService.change_role(user, 'accountant')
        assert updated.role == 'accountant'
    
    def test_search_users(self, users_batch):
        """تست جستجوی کاربران"""
        results = UserService.search_users(query='user')
        assert results.count() > 0


@pytest.mark.django_db
class TestProfileService:
    """
    تست‌های ProfileService
    """
    
    def test_calculate_completion_individual(self, user):
        """تست محاسبه درصد تکمیل حقیقی"""
        profile = ProfileFactory(
            user=user,
            national_code='1234567890',
            address='Test',
            postal_code='1234567890',
            tel='02112345678',
            is_completed=True
        )
        
        percentage = ProfileService.calculate_completion_percentage(profile)
        assert percentage > 0
        assert percentage <= 100


@pytest.mark.django_db
class TestWalletService:
    """
    تست‌های WalletService
    """
    
    def test_deposit(self, user):
        """تست واریز"""
        wallet = WalletFactory(user=user, balance=0)
        tx = WalletService.deposit(wallet, 10000)
        
        wallet.refresh_from_db()
        assert wallet.balance == 10000
        assert tx.transaction_type == 'deposit'
        assert tx.status == 'completed'
    
    def test_withdraw(self, user):
        """تست برداشت"""
        wallet = WalletFactory(user=user, balance=50000)
        tx = WalletService.withdraw(wallet, 20000)
        
        wallet.refresh_from_db()
        assert wallet.balance == 30000
        assert tx.transaction_type == 'withdraw'
    
    def test_transfer(self, user):
        """تست انتقال وجه"""
        user2 = UserFactory()
        wallet1 = WalletFactory(user=user, balance=50000)
        wallet2 = WalletFactory(user=user2, balance=0)
        
        tx1, tx2 = WalletService.transfer(wallet1, wallet2, 20000)
        
        wallet1.refresh_from_db()
        wallet2.refresh_from_db()
        
        assert wallet1.balance == 30000
        assert wallet2.balance == 20000
    
    def test_get_balance(self, user):
        """تست دریافت موجودی"""
        wallet = WalletFactory(user=user, balance=10000, blocked_balance=3000)
        balance_info = WalletService.get_balance(wallet)
        
        assert balance_info['balance'] == 10000
        assert balance_info['blocked_balance'] == 3000
        assert balance_info['available_balance'] == 7000