import logging
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum
from django.db import models as db_models
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.stock.models import Product, ProductImage
from apps.stock.serializers.product import (
    ProductSerializer,
    ProductListSerializer,
    ProductCreateSerializer,
    ProductMarketSerializer,
)
from apps.stock.permissions import CanManageStock, CanManageMarket

logger = logging.getLogger(__name__)


class ProductViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet مدیریت محصولات
    """
    queryset = Product.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['publish_to_market', 'remove_from_market']:
            return ProductMarketSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['publish_to_market', 'remove_from_market']:
            return [IsAuthenticated(), CanManageMarket()]
        return [IsAuthenticated(), CanManageStock()]

    def get_queryset(self):
        queryset = Product.objects.select_related(
            'brand', 'series', 'category'
        ).prefetch_related('images')

        # فیلترها
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand_id=brand)

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # جستجو
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(model_number__icontains=search) |
                Q(processor__icontains=search)
            )

        # فقط محصولات قابل فروش
        in_stock = self.request.query_params.get('in_stock')
        if in_stock:
            queryset = queryset.filter(
                inventory_items__status='in_stock'
            ).distinct()

        return queryset

    @action(detail=True, methods=['post'])
    def publish_to_market(self, request, pk=None):
        """انتشار محصول در مارکت"""
        product = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'product': product}
        )
        serializer.is_valid(raise_exception=True)

        try:
            qty = serializer.validated_data['market_quantity']
            product.allocate_to_market(qty)

            if serializer.validated_data.get('market_price'):
                product.market_price = serializer.validated_data['market_price']

            if serializer.validated_data.get('market_description'):
                product.market_description = serializer.validated_data['market_description']

            if serializer.validated_data.get('market_tags'):
                product.market_tags = serializer.validated_data['market_tags']

            product.market_status = 'published'
            product.save()

            logger.info(f"Product {product.sku} published to market: {qty} units")

            return Response({
                'message': _('Product published to marketplace.'),
                'market_quantity': product.market_quantity,
                'available_stock': product.available_stock,
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_from_market(self, request, pk=None):
        """حذف محصول از مارکت"""
        product = self.get_object()
        quantity = request.data.get('quantity', product.market_quantity)

        try:
            qty = int(quantity)
            product.return_from_market(qty)

            if product.market_quantity <= 0:
                product.market_status = 'draft'
                product.save()

            logger.info(f"Product {product.sku} removed from market: {qty} units")

            return Response({
                'message': _('Product removed from marketplace.'),
                'market_quantity': product.market_quantity,
                'available_stock': product.available_stock,
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """موجودی محصول در انبارهای مختلف"""
        product = self.get_object()
        items = product.inventory_items.select_related('warehouse').all()

        from apps.stock.serializers.inventory import InventoryItemSerializer
        serializer = InventoryItemSerializer(items, many=True)

        return Response({
            'product': ProductListSerializer(product).data,
            'total_stock': product.total_stock,
            'available_stock': product.available_stock,
            'market_quantity': product.market_quantity,
            'inventory_items': serializer.data,
        })

    @action(detail=False, methods=['get'])
    def market_products(self, request):
        """محصولات قابل نمایش در مارکت"""
        products = Product.objects.filter(
            is_active=True,
            is_market_visible=True,
            market_status='published',
            market_quantity__gt=0
        ).select_related('brand', 'category')

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """محصولات با موجودی کم"""
        products = Product.objects.filter(
            is_active=True,
            inventory_items__quantity__lte=db_models.F('min_stock_alert')
        ).distinct()

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """آپلود تصویر برای محصول"""
        product = self.get_object()
        image = request.FILES.get('image')

        if not image:
            return Response({'error': _('Image is required.')}, status=status.HTTP_400_BAD_REQUEST)

        is_main = request.data.get('is_main', False)

        # اگر main هست، بقیه رو false کن
        if is_main:
            ProductImage.objects.filter(product=product).update(is_main=False)

        img = ProductImage.objects.create(
            product=product,
            image=image,
            is_main=is_main,
            sort_order=ProductImage.objects.filter(product=product).count()
        )

        from apps.stock.serializers.product import ProductImageSerializer
        return Response(ProductImageSerializer(img).data, status=status.HTTP_201_CREATED)