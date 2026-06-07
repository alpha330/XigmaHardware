"""
API v1 URL Configuration
"""

from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'name': 'XigmaHardware Marketplace API',
        'version': 'v1',
        'endpoints': {
            'accounts': '/api/v1/accounts/',
            'stock': '/api/v1/stock/',
            'market': '/api/v1/market/',
            'basket': '/api/v1/basket/',
            'financial': '/api/v1/financial/',
            'payment': '/api/v1/payment/',
            'logistics': '/api/v1/logistics/',
            'support': '/api/v1/support/',
            'website': '/api/v1/website/',
            'swagger': '/swagger/',
            'redoc': '/redoc/',
        }
    })


app_name = 'api'

urlpatterns = [
    path('', api_root, name='api-root'),

    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('stock/', include('apps.stock.urls', namespace='stock')),
    path('market/', include('apps.market.urls', namespace='market')),
    path('basket/', include('apps.basket.urls', namespace='basket')),
    path('financial/', include('apps.financial.urls', namespace='financial')),
    path('payment/', include('apps.payment.urls', namespace='payment')),
    path('logistics/', include('apps.logistics.urls', namespace='logistics')),
    path('support/', include('apps.support.urls', namespace='support')),
    path('website/', include('apps.website.urls', namespace='website')),
]