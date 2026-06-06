import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.market.models import ProductMedia
from apps.market.serializers.media import (
    ProductMediaSerializer,
    ProductMediaCreateSerializer,
)

logger = logging.getLogger(__name__)


class MediaViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    ViewSet مدیریت مدیا (گالری تصاویر و ویدیوها)

    Actions:
    - list: مدیاهای یک محصول
    - create: آپلود مدیا
    - destroy: حذف مدیا
    - set_main: تنظیم به عنوان تصویر اصلی
    - reorder: تغییر ترتیب
    """
    queryset = ProductMedia.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductMediaCreateSerializer
        return ProductMediaSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = ProductMedia.objects.all()

        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        return queryset

    @action(detail=True, methods=['post'])
    def set_main(self, request, pk=None):
        """تنظیم به عنوان تصویر اصلی"""
        media = self.get_object()

        # غیرفعال کردن بقیه
        ProductMedia.objects.filter(product=media.product).update(is_main=False)

        # فعال کردن این
        media.is_main = True
        media.save()

        return Response({'message': _('Set as main image.')})

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """تغییر ترتیب"""
        items = request.data.get('items', [])

        for item in items:
            ProductMedia.objects.filter(id=item['id']).update(sort_order=item['sort_order'])

        return Response({'message': _('Order updated.')})

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """آپلود گروهی تصاویر"""
        product_id = request.data.get('product')
        images = request.FILES.getlist('images')

        if not product_id or not images:
            return Response(
                {'error': _('Product ID and images required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []
        for i, image in enumerate(images):
            media = ProductMedia.objects.create(
                product_id=product_id,
                media_type='gallery',
                image=image,
                sort_order=i,
                is_main=(i == 0),  # اولین تصویر = اصلی
            )
            created.append(ProductMediaSerializer(media, context={'request': request}).data)

        return Response({
            'message': _(f'{len(created)} images uploaded.'),
            'media': created,
        }, status=status.HTTP_201_CREATED)