from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.product import MarketProductViewSet
from .views.rating import RatingViewSet
from .views.review import ReviewViewSet
from .views.comment import CommentViewSet
from .views.media import MediaViewSet

router = DefaultRouter()
router.register(r'products', MarketProductViewSet, basename='market-product')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'media', MediaViewSet, basename='media')

app_name = 'market'

urlpatterns = [
    path('', include(router.urls)),
]