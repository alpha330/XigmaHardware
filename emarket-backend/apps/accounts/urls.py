"""
Accounts App URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
from .views.auth import (
    EmailRegisterView,
    MobileRegisterView,
    LoginView,
    LogoutView,
    EmailVerificationView,
    MobileVerificationView,
    RequestOTPView,
    VerifyOTPView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
)
from .views.user import UserViewSet
from .views.profile import ProfileViewSet
from .views.wallet import WalletViewSet
from .views.device import DeviceViewSet

# Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'wallets', WalletViewSet, basename='wallet')
router.register(r'devices', DeviceViewSet, basename='device')

app_name = 'accounts'

urlpatterns = [
    # ==================== AUTH ====================
    
    # Registration
    path('auth/register/email/',
         EmailRegisterView.as_view(),
         name='email-register'),
    path('auth/register/mobile/',
         MobileRegisterView.as_view(),
         name='mobile-register'),
    
    # Login/Logout
    path('auth/login/',
         LoginView.as_view(),
         name='login'),
    path('auth/logout/',
         LogoutView.as_view(),
         name='logout'),
    
    # JWT Tokens
    path('auth/token/refresh/',
         TokenRefreshView.as_view(),
         name='token-refresh'),
    path('auth/token/verify/',
         TokenVerifyView.as_view(),
         name='token-verify'),
    path('auth/token/blacklist/',
         TokenBlacklistView.as_view(),
         name='token-blacklist'),
    
    # Email Verification
    path('auth/verify/email/<str:token>/',
         EmailVerificationView.as_view(),
         name='verify-email'),
    path('auth/verify/email/resend/',
         EmailVerificationView.as_view(),
         name='resend-email-verification'),
    
    # Mobile/OTP Verification
    path('auth/otp/request/',
         RequestOTPView.as_view(),
         name='request-otp'),
    path('auth/otp/verify/',
         VerifyOTPView.as_view(),
         name='verify-otp'),
    path('auth/verify/mobile/',
         MobileVerificationView.as_view(),
         name='verify-mobile'),
    
    # Password Management
    path('auth/password/change/',
         ChangePasswordView.as_view(),
         name='change-password'),
    path('auth/password/reset/',
         PasswordResetRequestView.as_view(),
         name='password-reset-request'),
    path('auth/password/reset/confirm/',
         PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),
    
    # ==================== USER ====================
    
    # Current User
    path('me/',
         UserViewSet.as_view({
             'get': 'me',
             'put': 'me',
             'patch': 'me'
         }),
         name='user-me'),
    path('me/delete-account/',
         UserViewSet.as_view({'delete': 'delete_account'}),
         name='delete-account'),
    
    # ==================== PROFILE ====================
    
    # My Profile
    path('me/profile/',
         ProfileViewSet.as_view({
             'get': 'my_profile',
             'put': 'my_profile',
             'patch': 'my_profile'
         }),
         name='my-profile'),
    path('me/profile/switch-to-legal/',
         ProfileViewSet.as_view({'post': 'switch_to_legal'}),
         name='switch-to-legal'),
    path('me/profile/switch-to-individual/',
         ProfileViewSet.as_view({'post': 'switch_to_individual'}),
         name='switch-to-individual'),
    path('me/profile/check-completion/',
         ProfileViewSet.as_view({'get': 'check_completion'}),
         name='check-profile-completion'),
    
    # ==================== WALLET ====================
    
    # My Wallet
    path('me/wallet/',
         WalletViewSet.as_view({'get': 'my_wallet'}),
         name='my-wallet'),
    path('me/wallet/transactions/',
         WalletViewSet.as_view({'get': 'my_transactions'}),
         name='my-transactions'),
    path('me/wallet/deposit/',
         WalletViewSet.as_view({'post': 'deposit'}),
         name='wallet-deposit'),
    path('me/wallet/withdraw/',
         WalletViewSet.as_view({'post': 'withdraw'}),
         name='wallet-withdraw'),
    
    # ==================== DEVICES ====================
    
    # My Devices
    path('me/devices/',
         DeviceViewSet.as_view({'get': 'my_devices'}),
         name='my-devices'),
    path('me/devices/revoke-all-other/',
         DeviceViewSet.as_view({'post': 'revoke_all_other'}),
         name='revoke-all-other-devices'),
    path('me/devices/<uuid:pk>/trust/',
         DeviceViewSet.as_view({'post': 'trust_device'}),
         name='trust-device'),
    path('me/devices/<uuid:pk>/revoke/',
         DeviceViewSet.as_view({'post': 'revoke_device'}),
         name='revoke-device'),
    
    # ==================== ADMIN ====================
    
    # Admin User Management
    path('admin/users/',
         UserViewSet.as_view({'get': 'list'}),
         name='admin-users-list'),
    path('admin/users/<uuid:pk>/',
         UserViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update'
         }),
         name='admin-user-detail'),
    path('admin/users/<uuid:pk>/change-role/',
         UserViewSet.as_view({'post': 'change_role'}),
         name='admin-change-role'),
    path('admin/users/<uuid:pk>/toggle-active/',
         UserViewSet.as_view({'post': 'toggle_active'}),
         name='admin-toggle-active'),
    
    # Admin Profile Management
    path('admin/profiles/',
         ProfileViewSet.as_view({'get': 'list'}),
         name='admin-profiles-list'),
    path('admin/profiles/<uuid:pk>/',
         ProfileViewSet.as_view({'get': 'retrieve'}),
         name='admin-profile-detail'),
    
    # Admin Wallet Management
    path('admin/wallets/',
         WalletViewSet.as_view({'get': 'list'}),
         name='admin-wallets-list'),
    path('admin/wallets/<uuid:pk>/',
         WalletViewSet.as_view({'get': 'retrieve'}),
         name='admin-wallet-detail'),
    
    # Admin Device Management
    path('admin/devices/',
         DeviceViewSet.as_view({'get': 'list'}),
         name='admin-devices-list'),
    
    # ==================== ROUTER ====================
    path('', include(router.urls)),
]