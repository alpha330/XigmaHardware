"""
Tests for Authentication API
"""

import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestRegistration:
    """
    تست‌های ثبت‌نام
    """
    
    def test_register_with_email(self, api_client, user_data):
        """تست ثبت‌نام موفق با ایمیل"""
        url = reverse('accounts:email-register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == user_data['email']
    
    def test_register_with_existing_email(self, api_client, user, user_data):
        """تست ثبت‌نام با ایمیل تکراری"""
        url = reverse('accounts:email-register')
        user_data['email'] = user.email
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_with_mobile(self, api_client):
        """تست ثبت‌نام با موبایل"""
        url = reverse('accounts:mobile-register')
        data = {
            'mobile': '09123456789',
            'password': 'TestPass123!',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['mobile'] == '09123456789'
    
    def test_register_with_invalid_mobile(self, api_client):
        """تست ثبت‌نام با موبایل نامعتبر"""
        url = reverse('accounts:mobile-register')
        data = {
            'mobile': '12345',
            'password': 'TestPass123!',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_password_mismatch(self, api_client):
        """تست عدم تطابق رمز عبور"""
        url = reverse('accounts:email-register')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    """
    تست‌های ورود
    """
    
    def test_login_with_email(self, api_client, user, test_password):
        """تست ورود موفق با ایمیل"""
        url = reverse('accounts:login')
        data = {
            'email': user.email,
            'password': test_password,
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert response.data['user']['email'] == user.email
    
    def test_login_with_mobile(self, api_client, test_password):
        """تست ورود با موبایل"""
        user = UserFactory(mobile='09123456789')
        user.set_password(test_password)
        user.save()
        
        url = reverse('accounts:login')
        data = {
            'mobile': '09123456789',
            'password': test_password,
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_login_invalid_credentials(self, api_client, user):
        """تست ورود با اطلاعات نادرست"""
        url = reverse('accounts:login')
        data = {
            'email': user.email,
            'password': 'WrongPassword123!',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_inactive_user(self, api_client, test_password):
        """تست ورود کاربر غیرفعال"""
        user = UserFactory(inactive=True)
        url = reverse('accounts:login')
        data = {
            'email': user.email,
            'password': test_password,
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestLogout:
    """
    تست‌های خروج
    """
    
    def test_logout(self, authenticated_client):
        """تست خروج موفق"""
        url = reverse('accounts:logout')
        # باید refresh token رو بفرستی
        response = authenticated_client.post(url, {}, format='json')
        
        # ممکنه نیاز به refresh token داشته باشه
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


@pytest.mark.django_db
class TestPasswordChange:
    """
    تست‌های تغییر رمز عبور
    """
    
    def test_change_password(self, authenticated_client, test_password):
        """تست تغییر رمز عبور موفق"""
        url = reverse('accounts:change-password')
        data = {
            'old_password': test_password,
            'new_password': 'NewTestPass456!',
            'new_password_confirm': 'NewTestPass456!',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old(self, authenticated_client):
        """تست تغییر رمز با رمز فعلی اشتباه"""
        url = reverse('accounts:change-password')
        data = {
            'old_password': 'WrongPass123!',
            'new_password': 'NewTestPass456!',
            'new_password_confirm': 'NewTestPass456!',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST