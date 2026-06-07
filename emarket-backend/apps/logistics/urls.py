from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.address import AddressViewSet
from .views.courier import CourierViewSet
from .views.shipment import ShipmentViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'couriers', CourierViewSet, basename='courier')
router.register(r'shipments', ShipmentViewSet, basename='shipment')

app_name = 'logistics'

urlpatterns = [
    path('', include(router.urls)),

    # اضافی
    path('cost-estimate/',
         ShipmentViewSet.as_view({'post': 'cost_estimate'}),
         name='cost-estimate'),
]