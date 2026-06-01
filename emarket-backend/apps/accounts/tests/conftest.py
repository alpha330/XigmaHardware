"""
Pytest Configuration and Fixtures
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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
    """ساخت یک کاربر عادی"""
    from apps.accounts.tests.factories import UserFactory, ProfileFactory, WalletFactory
    
    user = UserFactory()
    ProfileFactory(user=user)
    WalletFactory(user=user)
    return user


@pytest.fixture
def admin_user(db):
    """ساخت کاربر ادمین"""
    from apps.accounts.tests.factories import UserFactory, ProfileFactory, WalletFactory
    
    user = UserFactory(role='super_admin', is_staff=True, is_superuser=True)
    ProfileFactory(user=user)
    WalletFactory(user=user)
    return user


@pytest.fixture
def users_batch(db):
    """ساخت 10 کاربر تستی"""
    from apps.accounts.tests.factories import UserFactory, ProfileFactory, WalletFactory
    
    users = []
    for i in range(10):
        user = UserFactory()
        ProfileFactory(user=user)
        WalletFactory(user=user)
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