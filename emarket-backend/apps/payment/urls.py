from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.payment import PaymentViewSet

router = DefaultRouter()
router.register(r'gateways', PaymentViewSet, basename='gateway')

app_name = 'payment'

urlpatterns = [
    path('', include(router.urls)),

    # Payment endpoints
    path('pay/', PaymentViewSet.as_view({'post': 'pay'}), name='pay'),
    path('pay/wallet/', PaymentViewSet.as_view({'post': 'pay_with_wallet'}), name='pay-wallet'),
    path('callback/<uuid:payment_log_id>/',
         PaymentViewSet.as_view({'get': 'callback', 'post': 'callback'}),
         name='callback'),
    path('verify/<uuid:payment_log_id>/',
         PaymentViewSet.as_view({'post': 'verify'}),
         name='verify'),
    path('status/<uuid:payment_log_id>/',
         PaymentViewSet.as_view({'get': 'payment_status'}),
         name='payment-status'),
    path('my-payments/',
         PaymentViewSet.as_view({'get': 'my_payments'}),
         name='my-payments'),
    path('active-gateways/',
         PaymentViewSet.as_view({'get': 'active_gateways'}),
         name='active-gateways'),
]