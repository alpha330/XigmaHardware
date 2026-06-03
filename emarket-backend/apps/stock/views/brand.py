import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.stock.models import Brand, BrandSeries
from apps.stock.serializers.brand import (
    BrandSerializer,
    BrandCreateSerializer,
    BrandSeriesSerializer,
    BrandSeriesCreateSerializer,
)
from apps.stock.permissions import CanManageStock

logger = logging.getLogger(__name__)


class BrandViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    """
    ViewSet مدیریت برندها
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return BrandCreateSerializer
        return BrandSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), CanManageStock()]

    @action(detail=True, methods=['get'])
    def series(self, request, pk=None):
        """سری‌های یک برند"""
        brand = self.get_object()
        series = brand.series.filter(is_active=True)
        serializer = BrandSeriesSerializer(series, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """محصولات یک برند"""
        brand = self.get_object()
        from apps.stock.serializers.product import ProductListSerializer

        products = brand.products.filter(is_active=True)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def partners(self, request):
        """برندهای طرف قرارداد"""
        partners = Brand.objects.filter(is_active=True, is_partner=True)
        serializer = self.get_serializer(partners, many=True)
        return Response(serializer.data)


class BrandSeriesViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    """
    ViewSet مدیریت سری برندها
    """
    queryset = BrandSeries.objects.filter(is_active=True)
    serializer_class = BrandSeriesSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return BrandSeriesCreateSerializer
        return BrandSeriesSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), CanManageStock()]

    def get_queryset(self):
        queryset = BrandSeries.objects.filter(is_active=True)
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand_id=brand)
        return queryset.select_related('brand')

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """محصولات یک سری"""
        series = self.get_object()
        from apps.stock.serializers.product import ProductListSerializer

        products = series.products.filter(is_active=True)
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)