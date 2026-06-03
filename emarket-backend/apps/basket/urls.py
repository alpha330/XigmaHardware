from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.cart import CartViewSet
from .views.wishlist import WishlistViewSet

router = DefaultRouter()
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')

app_name = 'basket'

urlpatterns = [
    path('', include(router.urls)),
]
