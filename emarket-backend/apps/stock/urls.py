from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WarehouseViewSet,
    ProductCategoryViewSet,
    BrandViewSet,
    BrandSeriesViewSet,
    ProductViewSet,
    InventoryViewSet,
    StockMovementViewSet,
)

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'series', BrandSeriesViewSet, basename='series')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory', InventoryViewSet, basename='inventory')
router.register(r'movements', StockMovementViewSet, basename='movement')

app_name = 'stock'

urlpatterns = [
    path('', include(router.urls)),
]