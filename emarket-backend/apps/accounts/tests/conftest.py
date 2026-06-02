"""
Pytest Configuration and Fixtures
نسخه model-bakery (ساده‌تر)
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from model_bakery import baker

User = get_user_model()


@pytest.fixture
def api_client():
    """API Client بدون احراز هویت"""
    return APIClient()


@pytest.fixture
def authenticated_client(user):
    """API Client با احراز هویت"""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    client.user = user
    return client


@pytest.fixture
def admin_client(admin_user):
    """API Client برای ادمین"""
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    client.user = admin_user
    return client


@pytest.fixture
def user(db):
    """
    ساخت یک کاربر عادی با model-bakery
    سریع و ساده
    """
    user = baker.make(
        'accounts.User',
        email='testuser@example.com',
        mobile='09123456789',
        first_name='Test',
        last_name='User',
        is_active=True,
        is_email_verified=True,
        is_mobile_verified=True,
        role='client',
    )
    user.set_password('TestPass123!')
    user.save()
    
    # ساخت پروفایل و کیف پول
    baker.make('accounts.Profile', user=user)
    baker.make('accounts.Wallet', user=user)
    
    return user


@pytest.fixture
def admin_user(db):
    """
    ساخت کاربر ادمین با model-bakery
    """
    admin = baker.make(
        'accounts.User',
        email='admin@example.com',
        mobile='09120000000',
        first_name='Admin',
        last_name='User',
        is_active=True,
        is_staff=True,
        is_superuser=True,
        is_email_verified=True,
        is_mobile_verified=True,
        role='super_admin',
    )
    admin.set_password('AdminPass123!')
    admin.save()
    
    # ساخت پروفایل و کیف پول
    baker.make('accounts.Profile', user=admin)
    baker.make('accounts.Wallet', user=admin, balance=9999999)
    
    return admin


@pytest.fixture
def users_batch(db):
    """
    ساخت 10 کاربر تستی با model-bakery
    """
    users = []
    for i in range(10):
        user = baker.make(
            'accounts.User',
            email=f'user{i}@example.com',
            mobile=f'09{i:09d}'[:11],
            first_name=f'User{i}',
            last_name='Test',
            is_active=True,
            is_email_verified=True,
        )
        user.set_password('TestPass123!')
        user.save()
        
        baker.make('accounts.Profile', user=user)
        baker.make('accounts.Wallet', user=user)
        
        users.append(user)
    
    return users


@pytest.fixture
def test_password():
    """رمز عبور تست"""
    return 'TestPass123!'


@pytest.fixture
def user_data(test_password):
    """داده‌های کاربر برای تست"""
    return {
        'email': 'testuser@example.com',
        'password': test_password,
        'password_confirm': test_password,
        'first_name': 'Test',
        'last_name': 'User',
        'mobile': '09123456789',
    }