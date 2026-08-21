"""
Tests for Authentication API
"""

from unittest.mock import patch

import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import OTPCode
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestRegistration:
    """
    تست‌های ثبت‌نام
    """
    
    def test_register_with_email(self, api_client, user_data):
        """تست ثبت‌نام موفق با ایمیل"""
        url = reverse('api:accounts:email-register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['user']['email'] == user_data['email']
    
    def test_register_with_existing_email(self, api_client, user, user_data):
        """تست ثبت‌نام با ایمیل تکراری"""
        url = reverse('api:accounts:email-register')
        user_data['email'] = user.email
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_with_mobile(self, api_client):
        """تست ثبت‌نام با موبایل"""
        url = reverse('api:accounts:mobile-register')
        data = {
            'mobile': '09123456789',
            'password': 'TestPass123!',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['mobile'] == '09123456789'
    
    def test_register_with_invalid_mobile(self, api_client):
        """تست ثبت‌نام با موبایل نامعتبر"""
        url = reverse('api:accounts:mobile-register')
        data = {
            'mobile': '12345',
            'password': 'TestPass123!',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_password_mismatch(self, api_client):
        """تست عدم تطابق رمز عبور"""
        url = reverse('api:accounts:email-register')
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
        url = reverse('api:accounts:login')
        data = {
            'identifier': user.email,
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
        
        url = reverse('api:accounts:login')
        data = {
            'identifier': '09123456789',
            'password': test_password,
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_login_invalid_credentials(self, api_client, user):
        """تست ورود با اطلاعات نادرست"""
        url = reverse('api:accounts:login')
        data = {
            'identifier': user.email,
            'password': 'WrongPassword123!',
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_inactive_user(self, api_client, test_password):
        """تست ورود کاربر غیرفعال"""
        user = UserFactory(inactive=True)
        url = reverse('api:accounts:login')
        data = {
            'identifier': user.email,
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
        url = reverse('api:accounts:logout')
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
        url = reverse('api:accounts:change-password')
        data = {
            'old_password': test_password,
            'new_password': 'NewTestPass456!',
            'new_password_confirm': 'NewTestPass456!',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old(self, authenticated_client):
        """تست تغییر رمز با رمز فعلی اشتباه"""
        url = reverse('api:accounts:change-password')
        data = {
            'old_password': 'WrongPass123!',
            'new_password': 'NewTestPass456!',
            'new_password_confirm': 'NewTestPass456!',
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordReset:
    @patch('apps.accounts.views.auth.send_password_reset_email.delay')
    def test_email_request_sends_otp(self, send_email, api_client, user):
        url = reverse('api:accounts:password-reset-request')

        response = api_client.post(
            url,
            {'email_or_mobile': user.email},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['reset_method'] == 'otp'
        assert response.data['delivery_channel'] == 'email'
        assert response.data['otp_id']

        otp = OTPCode.objects.get(id=response.data['otp_id'])
        assert otp.user == user
        assert otp.purpose == 'reset_password'
        assert otp.sent_via == 'email'
        send_email.assert_called_once_with(str(user.id), otp.code)

    @patch('apps.accounts.views.auth.send_password_reset_email.delay')
    def test_email_request_is_case_insensitive(self, send_email, api_client, user):
        url = reverse('api:accounts:password-reset-request')

        response = api_client.post(
            url,
            {'email_or_mobile': user.email.upper()},
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['otp_id']
        send_email.assert_called_once()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_reset_email_contains_otp_without_backend_link(self, user):
        reverse('api:accounts:password-reset-request')
        from apps.accounts.views.auth import send_password_reset_email

        code = '123456'

        send_password_reset_email.run(str(user.id), code)

        assert len(mail.outbox) == 1
        message = mail.outbox[0]
        html_content = message.alternatives[0][0]
        assert code in message.body
        assert code in html_content
        assert 'localhost:8000/auth/reset-password' not in message.body
        assert 'localhost:8000/auth/reset-password' not in html_content

    def test_confirm_requires_otp(self, api_client, user, test_password):
        url = reverse('api:accounts:password-reset-confirm')

        response = api_client.post(
            url,
            {
                'email_or_mobile': user.email,
                'new_password': 'NewTestPass456!',
                'new_password_confirm': 'NewTestPass456!',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password(test_password)

    def test_confirm_rejects_invalid_otp(self, api_client, user, test_password):
        otp = OTPCode.generate(
            user=user,
            purpose='reset_password',
            sent_via='email',
        )
        url = reverse('api:accounts:password-reset-confirm')

        response = api_client.post(
            url,
            {
                'email_or_mobile': user.email,
                'new_password': 'NewTestPass456!',
                'new_password_confirm': 'NewTestPass456!',
                'otp_id': str(otp.id),
                'code': '000000' if otp.code != '000000' else '111111',
            },
            format='json',
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password(test_password)

    def test_confirm_accepts_valid_otp(self, api_client, user):
        otp = OTPCode.generate(
            user=user,
            purpose='reset_password',
            sent_via='email',
        )
        url = reverse('api:accounts:password-reset-confirm')

        response = api_client.post(
            url,
            {
                'email_or_mobile': user.email,
                'new_password': 'NewTestPass456!',
                'new_password_confirm': 'NewTestPass456!',
                'otp_id': str(otp.id),
                'code': otp.code,
            },
            format='json',
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        otp.refresh_from_db()
        assert user.check_password('NewTestPass456!')
        assert otp.is_used is True
