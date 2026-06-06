import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.market.models import ProductReview, MarketProduct
from apps.market.serializers.review import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewListSerializer,
)
from apps.market.services.review_service import ReviewService

logger = logging.getLogger(__name__)


class ReviewViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """
    ViewSet ریویوهای محصولات

    Actions:
    - list: ریویوهای یک محصول
    - create: نوشتن ریویو
    - update: ویرایش ریویو
    - like: لایک/دیسلایک
    - my_review: ریویو من برای محصول
    """
    queryset = ProductReview.objects.filter(status='published')

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = ProductReview.objects.filter(status='published').select_related(
            'user', 'rating'
        ).prefetch_related('likes')

        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        sort = self.request.query_params.get('sort', '-created_at')
        if sort in ['-created_at', 'created_at', '-likes_count', 'likes_count']:
            queryset = queryset.order_by(sort)

        return queryset

    def perform_create(self, serializer):
        product = serializer.validated_data['product']

        try:
            review = ReviewService.create_review(
                product=product,
                user=self.request.user,
                title=serializer.validated_data['title'],
                body=serializer.validated_data['body'],
                pros=serializer.validated_data.get('pros', ''),
                cons=serializer.validated_data.get('cons', ''),
            )
            return review
        except ValueError as e:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError(str(e))

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """لایک یا دیسلایک"""
        review = self.get_object()
        is_like = request.data.get('is_like', True)

        result = ReviewService.like_review(review, request.user, is_like)

        return Response({
            'message': _('Like updated.'),
            **result,
        })

    @action(detail=False, methods=['get'])
    def my_review(self, request):
        """ریویو من برای یک محصول"""
        product_id = request.query_params.get('product')

        if not product_id:
            return Response({'error': _('Product ID required.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = MarketProduct.objects.get(id=product_id)
        except MarketProduct.DoesNotExist:
            return Response({'error': _('Product not found.')}, status=status.HTTP_404_NOT_FOUND)

        review = ReviewService.get_user_review_for_product(product, request.user)

        if review:
            return Response(ReviewSerializer(review, context={'request': request}).data)

        return Response({'has_review': False})

    @action(detail=True, methods=['delete'])
    def delete_review(self, request, pk=None):
        """حذف ریویو"""
        review = self.get_object()

        if review.user != request.user:
            return Response({'error': _('Not your review.')}, status=status.HTTP_403_FORBIDDEN)

        ReviewService.delete_review(review)
        return Response({'message': _('Review deleted.')})