import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.stock.models import Warehouse
from apps.stock.serializers.warehouse import (
    WarehouseSerializer,
    WarehouseListSerializer,
    WarehouseCreateSerializer,
)
from apps.stock.permissions import CanManageWarehouse, IsWarehouseStaff
from django.db import models as db_models

logger = logging.getLogger(__name__)


class WarehouseViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    ViewSet مدیریت انبارها

    دسترسی:
    - super_admin: همه کار
    - stock_keeper: انبارهای خودش
    - بقیه: فقط لیست انبارهای عمومی
    """
    queryset = Warehouse.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return WarehouseListSerializer
        elif self.action == 'create':
            return WarehouseCreateSerializer
        return WarehouseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanManageWarehouse()]
        elif self.action in ['add_stock', 'remove_stock', 'transfer_stock']:
            return [IsAuthenticated(), IsWarehouseStaff()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        # ادمین همه رو می‌بینه
        if user.is_superuser or user.role in ['super_admin', 'accountant']:
            return Warehouse.objects.all()

        # انباردار فقط انبارهای خودش
        if user.role == 'stock_keeper':
            return Warehouse.objects.filter(
                db_models.Q(manager=user) | db_models.Q(staff=user)
            )

        # دیگران فقط انبارهای عمومی
        return Warehouse.objects.filter(is_public=True, is_active=True)

    @action(detail=True, methods=['get'])
    def sub_warehouses(self, request, pk=None):
        """لیست انبارهای فرعی"""
        warehouse = self.get_object()
        subs = warehouse.sub_warehouses.filter(is_active=True)
        serializer = WarehouseListSerializer(subs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """موجودی انبار"""
        warehouse = self.get_object()
        items = warehouse.inventory_items.select_related('product').all()

        from apps.stock.serializers.inventory import InventoryItemSerializer
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = InventoryItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stock_summary(self, request, pk=None):
        """خلاصه موجودی انبار"""
        warehouse = self.get_object()

        from django.db.models import Sum, Count
        items = warehouse.inventory_items

        summary = {
            'total_products': items.count(),
            'total_quantity': items.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'total_reserved': items.aggregate(Sum('reserved_quantity'))['reserved_quantity__sum'] or 0,
            'available': (items.aggregate(Sum('quantity'))['quantity__sum'] or 0) -
                         (items.aggregate(Sum('reserved_quantity'))['reserved_quantity__sum'] or 0),
            'low_stock_items': items.filter(
                models.Q(quantity__lte=models.F('minimum_quantity'))
            ).count(),
            'by_status': {
                status: items.filter(status=status).count()
                for status in ['in_stock', 'reserved', 'in_transit', 'damaged']
            },
            'utilization': {
                'percent': round((warehouse.current_items / warehouse.capacity * 100), 1)
                if warehouse.capacity > 0 else 0,
                'current': warehouse.current_items,
                'max': warehouse.capacity,
            }
        }

        return Response(summary)

    @action(detail=False, methods=['get'])
    def my_warehouses(self, request):
        """انبارهای من (برای انباردار)"""
        user = request.user
        warehouses = Warehouse.objects.filter(
            db_models.Q(manager=user) | db_models.Q(staff=user),
            is_active=True
        )
        serializer = WarehouseListSerializer(warehouses, many=True)
        return Response(serializer.data)