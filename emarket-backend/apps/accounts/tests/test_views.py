"""
Tests for Views/ViewSets
"""

import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestUserViewSet:
    """
    تست‌های UserViewSet
    """
    
    def test_get_me(self, authenticated_client, user):
        """تست دریافت پروفایل خود"""
        url = reverse('accounts:user-me')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == user.email
    
    def test_update_me(self, authenticated_client, user):
        """تست به‌روزرسانی پروفایل خود"""
        url = reverse('accounts:user-me')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # بررسی ذخیره شدن
        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'
    
    def test_get_me_unauthenticated(self, api_client):
        """تست دسترسی بدون احراز هویت"""
        url = reverse('accounts:user-me')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_admin_list_users(self, admin_client, users_batch):
        """تست لیست کاربران توسط ادمین"""
        url = reverse('accounts:admin-users-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_non_admin_list_users(self, authenticated_client):
        """تست دسترسی غیرمجاز به لیست کاربران"""
        url = reverse('accounts:admin-users-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_change_role(self, admin_client, user):
        """تست تغییر نقش کاربر توسط ادمین"""
        url = reverse('accounts:admin-change-role', kwargs={'pk': user.id})
        data = {'role': 'accountant'}
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.role == 'accountant'


@pytest.mark.django_db
class TestProfileViewSet:
    """
    تست‌های ProfileViewSet
    """
    
    def test_get_my_profile(self, authenticated_client, user):
        """تست دریافت پروفایل خود"""
        url = reverse('accounts:my-profile')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'profile' in response.data
    
    def test_update_my_profile(self, authenticated_client, user):
        """تست به‌روزرسانی پروفایل"""
        url = reverse('accounts:my-profile')
        data = {
            'address': 'New Test Address',
            'postal_code': '1234567890',
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        user.profile.refresh_from_db()
        assert user.profile.address == 'New Test Address'
    
    def test_switch_to_legal(self, authenticated_client, user):
        """تست تغییر پروفایل به حقوقی"""
        url = reverse('accounts:switch-to-legal')
        data = {
            'company_name': 'Test Company LLC',
            'national_id': '12345678901',
            'economic_code': '123456789012',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        user.profile.refresh_from_db()
        assert user.profile.is_legal is True
        assert user.profile.company_name == 'Test Company LLC'
    
    def test_check_completion(self, authenticated_client, user):
        """تست بررسی تکمیل پروفایل"""
        url = reverse('accounts:check-profile-completion')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'is_completed' in response.data
        assert 'missing_fields' in response.data


@pytest.mark.django_db
class TestWalletViewSet:
    """
    تست‌های WalletViewSet
    """
    
    def test_get_my_wallet(self, authenticated_client, user):
        """تست دریافت کیف پول خود"""
        url = reverse('accounts:my-wallet')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'wallet' in response.data
        assert 'balance' in response.data
    
    def test_deposit(self, authenticated_client, user):
        """تست واریز به کیف پول"""
        initial_balance = user.wallet.balance
        
        url = reverse('accounts:wallet-deposit')
        data = {
            'amount': 50000,
            'description': 'Test deposit',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        user.wallet.refresh_from_db()
        assert user.wallet.balance == initial_balance + 50000
    
    def test_withdraw(self, authenticated_client, user):
        """تست برداشت از کیف پول"""
        user.wallet.balance = 100000
        user.wallet.save()
        
        url = reverse('accounts:wallet-withdraw')
        data = {
            'amount': 30000,
            'description': 'Test withdrawal',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        user.wallet.refresh_from_db()
        assert user.wallet.balance == 70000
    
    def test_withdraw_insufficient(self, authenticated_client, user):
        """تست برداشت بیش از موجودی"""
        user.wallet.balance = 10000
        user.wallet.save()
        
        url = reverse('accounts:wallet-withdraw')
        data = {
            'amount': 50000,
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_my_transactions(self, authenticated_client, user):
        """تست دریافت تراکنش‌ها"""
        url = reverse('accounts:my-transactions')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeviceViewSet:
    """
    تست‌های DeviceViewSet
    """
    
    def test_get_my_devices(self, authenticated_client, user):
        """تست دریافت دستگاه‌ها"""
        url = reverse('accounts:my-devices')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'devices' in response.data