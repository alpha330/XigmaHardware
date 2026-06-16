from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.invoice import InvoiceViewSet
from .views.transaction import TransactionViewSet
from .views.report import ReportViewSet
from .views.coupon import CouponViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'coupons', CouponViewSet, basename='coupon')

app_name = 'financial'

urlpatterns = [
    path('', include(router.urls)),
]