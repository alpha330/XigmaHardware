"""
API Root View - نسخه نهایی با ۹ اپلیکیشن
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API Root - نمایش همه endpoint های موجود
    """
    api_info = {
        'name': 'XigmaHardware Marketplace API',
        'version': 'v1',
        'description': 'Welcome to XigmaHardware Marketplace API',
        'environment': getattr(settings, 'RUN_AS', 'dev'),
        'documentation': {
            'swagger': request.build_absolute_uri('/swagger/'),
            'redoc': request.build_absolute_uri('/redoc/'),
        },
        'endpoints': {
            'accounts': {
                'base': request.build_absolute_uri('/api/v1/accounts/'),
                'description': '👤 User management, authentication, profiles, wallets',
                'auth': {
                    'register_email': request.build_absolute_uri('/api/v1/accounts/auth/register/email/'),
                    'register_mobile': request.build_absolute_uri('/api/v1/accounts/auth/register/mobile/'),
                    'login': request.build_absolute_uri('/api/v1/accounts/auth/login/'),
                    'logout': request.build_absolute_uri('/api/v1/accounts/auth/logout/'),
                    'token_refresh': request.build_absolute_uri('/api/v1/accounts/auth/token/refresh/'),
                    'otp_request': request.build_absolute_uri('/api/v1/accounts/auth/otp/request/'),
                    'otp_verify': request.build_absolute_uri('/api/v1/accounts/auth/otp/verify/'),
                },
                'user': {
                    'me': request.build_absolute_uri('/api/v1/accounts/me/'),
                    'profile': request.build_absolute_uri('/api/v1/accounts/me/profile/'),
                    'wallet': request.build_absolute_uri('/api/v1/accounts/me/wallet/'),
                    'devices': request.build_absolute_uri('/api/v1/accounts/me/devices/'),
                },
            },
            'stock': {
                'base': request.build_absolute_uri('/api/v1/stock/'),
                'description': '📦 Warehouse management, products, inventory, categories',
                'warehouses': request.build_absolute_uri('/api/v1/stock/warehouses/'),
                'products': request.build_absolute_uri('/api/v1/stock/products/'),
                'categories': request.build_absolute_uri('/api/v1/stock/categories/'),
                'brands': request.build_absolute_uri('/api/v1/stock/brands/'),
                'inventory': request.build_absolute_uri('/api/v1/stock/inventory/'),
            },
            'market': {
                'base': request.build_absolute_uri('/api/v1/market/'),
                'description': '🛒 Online marketplace, product listings, reviews, ratings',
                'products': request.build_absolute_uri('/api/v1/market/products/'),
                'reviews': request.build_absolute_uri('/api/v1/market/reviews/'),
                'ratings': request.build_absolute_uri('/api/v1/market/ratings/'),
                'comments': request.build_absolute_uri('/api/v1/market/comments/'),
                'media': request.build_absolute_uri('/api/v1/market/media/'),
                'featured': request.build_absolute_uri('/api/v1/market/products/featured/'),
                'bestsellers': request.build_absolute_uri('/api/v1/market/products/bestsellers/'),
                'compare': request.build_absolute_uri('/api/v1/market/products/compare/'),
            },
            'basket': {
                'base': request.build_absolute_uri('/api/v1/basket/'),
                'description': '🧺 Shopping cart and wishlist management',
                'my_cart': request.build_absolute_uri('/api/v1/basket/carts/my_cart/'),
                'add_item': request.build_absolute_uri('/api/v1/basket/carts/add_item/'),
                'wishlists': request.build_absolute_uri('/api/v1/basket/wishlists/'),
            },
            'financial': {
                'base': request.build_absolute_uri('/api/v1/financial/'),
                'description': '💰 Invoices, transactions, financial reports',
                'invoices': request.build_absolute_uri('/api/v1/financial/invoices/'),
                'transactions': request.build_absolute_uri('/api/v1/financial/transactions/'),
                'reports': request.build_absolute_uri('/api/v1/financial/reports/'),
                'create_from_cart': request.build_absolute_uri('/api/v1/financial/invoices/create_from_cart/'),
                'wallet_charge': request.build_absolute_uri('/api/v1/financial/invoices/wallet_charge/'),
            },
            'payment': {
                'base': request.build_absolute_uri('/api/v1/payment/'),
                'description': '💳 Payment gateways (PayPing, wallet, ...)',
                'pay': request.build_absolute_uri('/api/v1/payment/pay/'),
                'wallet_pay': request.build_absolute_uri('/api/v1/payment/pay/wallet/'),
                'verify': request.build_absolute_uri('/api/v1/payment/verify/{id}/'),
                'active_gateways': request.build_absolute_uri('/api/v1/payment/active-gateways/'),
            },
            'logistics': {
                'base': request.build_absolute_uri('/api/v1/logistics/'),
                'description': '🚚 Shipping, addresses, couriers (Internal + Alopeyk + SnappBox)',
                'addresses': request.build_absolute_uri('/api/v1/logistics/addresses/'),
                'default_address': request.build_absolute_uri('/api/v1/logistics/addresses/default/'),
                'couriers': request.build_absolute_uri('/api/v1/logistics/couriers/'),
                'nearby_couriers': request.build_absolute_uri('/api/v1/logistics/couriers/nearby/'),
                'shipments': request.build_absolute_uri('/api/v1/logistics/shipments/'),
                'my_shipments': request.build_absolute_uri('/api/v1/logistics/shipments/my_shipments/'),
                'cost_estimate': request.build_absolute_uri('/api/v1/logistics/shipments/cost_estimate/'),
                'tracking': request.build_absolute_uri('/api/v1/logistics/shipments/{id}/tracking/'),
            },
            'support': {
                'base': request.build_absolute_uri('/api/v1/support/'),
                'description': '🎧 Support tickets, warranty, live chat, FAQ',
                'tickets': {
                    'list': request.build_absolute_uri('/api/v1/support/tickets/'),
                    'my_tickets': request.build_absolute_uri('/api/v1/support/tickets/my_tickets/'),
                    'create': request.build_absolute_uri('/api/v1/support/tickets/'),
                    'stats': request.build_absolute_uri('/api/v1/support/tickets/stats/'),
                },
                'warranties': {
                    'list': request.build_absolute_uri('/api/v1/support/warranties/'),
                    'my_warranties': request.build_absolute_uri('/api/v1/support/warranties/my_warranties/'),
                    'check': request.build_absolute_uri('/api/v1/support/warranties/check/'),
                    'claim': request.build_absolute_uri('/api/v1/support/warranties/{id}/claim/'),
                },
                'chat': {
                    'start': request.build_absolute_uri('/api/v1/support/chats/start/'),
                    'active': request.build_absolute_uri('/api/v1/support/chats/active/'),
                    'send': request.build_absolute_uri('/api/v1/support/chats/{id}/send/'),
                },
                'faq': {
                    'list': request.build_absolute_uri('/api/v1/support/faqs/'),
                    'categories': request.build_absolute_uri('/api/v1/support/faqs/categories/'),
                    'search': request.build_absolute_uri('/api/v1/support/faqs/?search=keyword'),
                },
            },
            # 'website': {
            #     'base': request.build_absolute_uri('/api/v1/website/'),
            #     'description': '🌐 Website pages, articles, news, contact',
            #     'pages': {
            #         'about': request.build_absolute_uri('/api/v1/website/pages/?type=about'),
            #         'terms': request.build_absolute_uri('/api/v1/website/pages/?type=terms'),
            #         'privacy': request.build_absolute_uri('/api/v1/website/pages/?type=privacy'),
            #     },
            #     'articles': {
            #         'list': request.build_absolute_uri('/api/v1/website/articles/'),
            #         'featured': request.build_absolute_uri('/api/v1/website/articles/?status=published'),
            #     },
            #     'news': {
            #         'list': request.build_absolute_uri('/api/v1/website/news/'),
            #         'pinned': request.build_absolute_uri('/api/v1/website/news/?status=pinned'),
            #     },
            #     'contact': {
            #         'send': request.build_absolute_uri('/api/v1/website/contact/'),
            #         'newsletter': request.build_absolute_uri('/api/v1/website/newsletter/subscribe/'),
            #     },
            # },
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
        'features': {
            'user_roles': ['super_admin', 'client', 'accountant', 'courier', 'stock_keeper'],
            'warehouse_types': ['main', 'sub', 'specialized', 'temporary'],
            'product_conditions': ['new', 'like_new', 'used', 'refurbished', 'damaged'],
            'rating_categories': ['value_for_money', 'quality', 'performance', 'overall'],
            'payment_gateways': ['payping', 'wallet', 'zarinpal (future)', 'crypto (future)'],
            'courier_services': ['internal', 'alopeyk', 'snappbox', 'post', 'tipax'],
            'support': ['tickets', 'warranty', 'live_chat', 'faq'],
            'reports': ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'],
            'email_templates': 'XigmaHardware branded emails for all modules',
            'sms': 'Coming soon',
        },
        'status': 'operational',
        'timestamp': __import__('django').utils.timezone.now().isoformat(),
        'total_endpoints': '290+',
        'apps': 9,
    }

    return Response(api_info)