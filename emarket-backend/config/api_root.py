"""
API Root View
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.urls import reverse
from django.conf import settings


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API Root - نمایش همه endpoint های موجود
    """
    api_info = {
        'name': 'Marketplace API',
        'version': 'v1',
        'description': 'Welcome to Marketplace API',
        'environment': settings.ENVIRONMENT,
        'documentation': {
            'swagger': request.build_absolute_uri('/swagger/'),
            'redoc': request.build_absolute_uri('/redoc/'),
        },
        'endpoints': {
            'accounts': {
                'base': request.build_absolute_uri('/api/v1/accounts/'),
                'auth': {
                    'register_email': request.build_absolute_uri('/api/v1/accounts/auth/register/email/'),
                    'register_mobile': request.build_absolute_uri('/api/v1/accounts/auth/register/mobile/'),
                    'login': request.build_absolute_uri('/api/v1/accounts/auth/login/'),
                    'logout': request.build_absolute_uri('/api/v1/accounts/auth/logout/'),
                    'refresh_token': request.build_absolute_uri('/api/v1/accounts/auth/token/refresh/'),
                    'verify_token': request.build_absolute_uri('/api/v1/accounts/auth/token/verify/'),
                    'otp_request': request.build_absolute_uri('/api/v1/accounts/auth/otp/request/'),
                    'otp_verify': request.build_absolute_uri('/api/v1/accounts/auth/otp/verify/'),
                    'change_password': request.build_absolute_uri('/api/v1/accounts/auth/password/change/'),
                    'reset_password_request': request.build_absolute_uri('/api/v1/accounts/auth/password/reset/'),
                    'reset_password_confirm': request.build_absolute_uri('/api/v1/accounts/auth/password/reset/confirm/'),
                },
                'user': {
                    'me': request.build_absolute_uri('/api/v1/accounts/me/'),
                    'delete_account': request.build_absolute_uri('/api/v1/accounts/me/delete-account/'),
                },
                'profile': {
                    'my_profile': request.build_absolute_uri('/api/v1/accounts/me/profile/'),
                    'switch_to_legal': request.build_absolute_uri('/api/v1/accounts/me/profile/switch-to-legal/'),
                    'switch_to_individual': request.build_absolute_uri('/api/v1/accounts/me/profile/switch-to-individual/'),
                    'check_completion': request.build_absolute_uri('/api/v1/accounts/me/profile/check-completion/'),
                },
                'wallet': {
                    'my_wallet': request.build_absolute_uri('/api/v1/accounts/me/wallet/'),
                    'transactions': request.build_absolute_uri('/api/v1/accounts/me/wallet/transactions/'),
                    'deposit': request.build_absolute_uri('/api/v1/accounts/me/wallet/deposit/'),
                    'withdraw': request.build_absolute_uri('/api/v1/accounts/me/wallet/withdraw/'),
                },
                'devices': {
                    'my_devices': request.build_absolute_uri('/api/v1/accounts/me/devices/'),
                    'revoke_all_other': request.build_absolute_uri('/api/v1/accounts/me/devices/revoke-all-other/'),
                },
                'admin': {
                    'users_list': request.build_absolute_uri('/api/v1/accounts/admin/users/'),
                    'profiles_list': request.build_absolute_uri('/api/v1/accounts/admin/profiles/'),
                    'wallets_list': request.build_absolute_uri('/api/v1/accounts/admin/wallets/'),
                    'devices_list': request.build_absolute_uri('/api/v1/accounts/admin/devices/'),
                },
            },
        },
        'authentication': {
            'type': 'JWT (JSON Web Token)',
            'header': 'Authorization: Bearer <access_token>',
            'refresh': 'POST /api/v1/accounts/auth/token/refresh/',
            'lifetime': {
                'access': '1 hour',
                'refresh': '7 days',
            },
        },
        'response_format': {
            'success': {
                'status': 'success',
                'data': {},
                'message': 'Operation successful'
            },
            'error': {
                'status': 'error',
                'error': {
                    'code': 'error_code',
                    'message': 'Error description',
                    'details': {}
                }
            }
        },
        'status': 'operational',
        'timestamp': __import__('django').utils.timezone.now().isoformat(),
    }
    
    return Response(api_info)