import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.market.models import ProductRating, MarketProduct
from apps.market.serializers.rating import (
    RatingSerializer,
    RatingCreateSerializer,
)
from apps.market.services.rating_service import RatingService

logger = logging.getLogger(__name__)


class RatingViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """
    ViewSet امتیازدهی به محصولات

    Actions:
    - list: امتیازات یک محصول
    - create: ثبت/بروزرسانی امتیاز
    - my_rating: امتیاز من برای محصول
    - summary: خلاصه امتیازات محصول
    """
    queryset = ProductRating.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return RatingCreateSerializer
        return RatingSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = ProductRating.objects.filter(is_active=True)

        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        return queryset.select_related('user')

    def create(self, request, *args, **kwargs):
        """ثبت یا بروزرسانی امتیاز"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = request.data.get('product')

        try:
            product = MarketProduct.objects.get(id=product_id, is_active=True)
        except MarketProduct.DoesNotExist:
            return Response(
                {'error': _('Product not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            rating, created = RatingService.rate_product(
                product=product,
                user=request.user,
                value_for_money=serializer.validated_data['value_for_money'],
                quality=serializer.validated_data['quality'],
                performance=serializer.validated_data['performance'],
                overall=serializer.validated_data['overall'],
            )

            return Response({
                'message': _('Rating saved.'),
                'rating': RatingSerializer(rating, context={'request': request}).data,
                'created': created,
                'product_rating': {
                    'avg': float(product.avg_rating),
                    'count': product.rating_count,
                }
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_rating(self, request):
        """امتیاز من برای یک محصول"""
        product_id = request.query_params.get('product')

        if not product_id:
            return Response({'error': _('Product ID required.')}, status=status.HTTP_400_BAD_REQUEST)

        rating = RatingService.get_user_rating(
            product_id=product_id,
            user=request.user,
        )

        if not rating:
            # باید product رو از id بگیریم
            try:
                product = MarketProduct.objects.get(id=product_id)
            except MarketProduct.DoesNotExist:
                return Response({'error': _('Product not found.')}, status=status.HTTP_404_NOT_FOUND)

            rating = RatingService.get_user_rating(product, request.user)

        if rating:
            return Response(RatingSerializer(rating, context={'request': request}).data)

        return Response({'has_rating': False})

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """خلاصه امتیازات محصول"""
        product_id = request.query_params.get('product')

        if not product_id:
            return Response({'error': _('Product ID required.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = MarketProduct.objects.get(id=product_id)
        except MarketProduct.DoesNotExist:
            return Response({'error': _('Product not found.')}, status=status.HTTP_404_NOT_FOUND)

        summary = RatingService.get_rating_summary(product)
        return Response(summary)

    @action(detail=False, methods=['delete'])
    def delete_my_rating(self, request):
        """حذف امتیاز من"""
        product_id = request.data.get('product')

        if not product_id:
            return Response({'error': _('Product ID required.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = MarketProduct.objects.get(id=product_id)
        except MarketProduct.DoesNotExist:
            return Response({'error': _('Product not found.')}, status=status.HTTP_404_NOT_FOUND)

        deleted = RatingService.delete_rating(product, request.user)

        if deleted:
            return Response({'message': _('Rating deleted.')})

        return Response({'message': _('No rating to delete.')})