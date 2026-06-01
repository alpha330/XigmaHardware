"""
API v1 URL Configuration
"""

from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Accounts App
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    
    # Future Apps
    # path('market/', include('apps.market.urls', namespace='market')),
    # path('stock/', include('apps.stock.urls', namespace='stock')),
    # path('financial/', include('apps.financial.urls', namespace='financial')),
    # path('payment/', include('apps.payment.urls', namespace='payment')),
    # path('basket/', include('apps.basket.urls', namespace='basket')),
    
    # API Root
    path('', include('config.api_root')),
]