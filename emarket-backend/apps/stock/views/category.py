import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.stock.models import ProductCategory
from apps.stock.serializers.category import (
    ProductCategorySerializer,
    ProductCategoryTreeSerializer,
    ProductCategoryCreateSerializer,
)
from apps.stock.permissions import CanManageStock

logger = logging.getLogger(__name__)


class ProductCategoryViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """
    ViewSet دسته‌بندی محصولات

    سطوح:
    1. Condition (نو/دسته دو)
    2. Usage (سرور/خانگی/پرتابل)
    3. Brand
    4. Type
    5. Series
    """
    queryset = ProductCategory.objects.all()

    def get_serializer_class(self):
        if self.action == 'tree':
            return ProductCategoryTreeSerializer
        elif self.action == 'create':
            return ProductCategoryCreateSerializer
        return ProductCategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'tree']:
            return [AllowAny()]
        return [IsAuthenticated(), CanManageStock()]

    def get_queryset(self):
        queryset = ProductCategory.objects.filter(is_active=True)

        # فیلتر بر اساس سطح
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)

        # فیلتر بر اساس parent
        parent = self.request.query_params.get('parent')
        if parent:
            queryset = queryset.filter(parent_id=parent)

        # فقط ریشه‌ها
        root = self.request.query_params.get('root')
        if root:
            queryset = queryset.filter(parent__isnull=True)

        return queryset.select_related('parent')

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """دریافت ساختار درختی کامل"""
        roots = ProductCategory.objects.filter(
            parent__isnull=True,
            is_active=True
        )
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """دریافت زیرمجموعه‌های یک دسته"""
        category = self.get_object()
        children = category.children.filter(is_active=True)
        serializer = ProductCategorySerializer(children, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """محصولات این دسته و زیرمجموعه‌ها"""
        category = self.get_object()
        descendants = category.get_descendants(include_self=True)

        from apps.stock.models import Product
        from apps.stock.serializers.product import ProductListSerializer

        products = Product.objects.filter(
            category__in=descendants,
            is_active=True
        )

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def conditions(self, request):
        """فقط دسته‌بندی‌های وضعیت (نو/دسته دو)"""
        conditions = ProductCategory.objects.filter(
            category_type='condition',
            is_active=True
        )
        serializer = ProductCategorySerializer(conditions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def usages(self, request):
        """فقط دسته‌بندی‌های کاربری (سرور/خانگی/...)"""
        condition = request.query_params.get('condition')
        queryset = ProductCategory.objects.filter(
            category_type='usage',
            is_active=True
        )
        if condition:
            queryset = queryset.filter(parent__slug=condition)
        serializer = ProductCategorySerializer(queryset, many=True)
        return Response(serializer.data)