import logging
from django.utils.translation import gettext_lazy as _
from django.db import models as db_models
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.stock.models import InventoryItem, StockMovement, Warehouse
from apps.stock.serializers.inventory import (
    InventoryItemSerializer,
    InventoryCreateSerializer,
    StockMovementSerializer,
    StockTransferSerializer,
)
from apps.stock.permissions import IsWarehouseStaff, CanManageStock

logger = logging.getLogger(__name__)


class InventoryViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    ViewSet مدیریت موجودی انبار
    """
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return InventoryCreateSerializer
        elif self.action == 'transfer':
            return StockTransferSerializer
        return InventoryItemSerializer

    def get_permissions(self):
        return [IsAuthenticated(), IsWarehouseStaff()]

    def get_queryset(self):
        user = self.request.user
        queryset = InventoryItem.objects.select_related(
            'warehouse', 'product', 'product__brand'
        )

        # فیلتر بر اساس انبار
        warehouse = self.request.query_params.get('warehouse')
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)

        # فیلتر بر اساس محصول
        product = self.request.query_params.get('product')
        if product:
            queryset = queryset.filter(product_id=product)

        # فیلتر وضعیت
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # موجودی کم
        low_stock = self.request.query_params.get('low_stock')
        if low_stock:
            queryset = queryset.filter(
                db_models.Q(quantity__lte=db_models.F('minimum_quantity'))
            )

        # اگر انباردار هست، فقط انبارهای خودش
        if user.role == 'stock_keeper' and not user.is_superuser:
            queryset = queryset.filter(
                db_models.Q(warehouse__manager=user) |
                db_models.Q(warehouse__staff=user)
            )

        return queryset

    def perform_create(self, serializer):
        item = serializer.save()

        # ثبت حرکت
        StockMovement.objects.create(
            inventory_item=item,
            movement_type='in',
            quantity=item.quantity,
            from_warehouse=None,
            to_warehouse=item.warehouse,
            reference=f"INIT-{item.batch_number or item.id}",
            performed_by=self.request.user
        )

        # آپدیت موجودی انبار
        item.warehouse.current_items = item.warehouse.inventory_items.aggregate(
            total=db_models.Sum('quantity')
        )['total'] or 0
        item.warehouse.save(update_fields=['current_items'])

        logger.info(f"Stock added: {item.product.sku} x{item.quantity} @ {item.warehouse.code}")

    def perform_update(self, serializer):
        old_item = self.get_object()
        old_qty = old_item.quantity
        new_item = serializer.save()
        new_qty = new_item.quantity

        if old_qty != new_qty:
            diff = new_qty - old_qty
            StockMovement.objects.create(
                inventory_item=new_item,
                movement_type='adjustment',
                quantity=abs(diff),
                from_warehouse=new_item.warehouse if diff < 0 else None,
                to_warehouse=new_item.warehouse if diff > 0 else None,
                reference=f"ADJ-{new_item.id}",
                notes=f"Adjusted from {old_qty} to {new_qty}",
                performed_by=self.request.user
            )

    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """افزایش موجودی"""
        item = self.get_object()
        quantity = request.data.get('quantity', 0)

        try:
            qty = int(quantity)
            if qty <= 0:
                raise ValueError('Quantity must be positive')

            item.add_stock(qty)

            # ثبت حرکت
            StockMovement.objects.create(
                inventory_item=item,
                movement_type='in',
                quantity=qty,
                to_warehouse=item.warehouse,
                reference=request.data.get('reference', ''),
                notes=request.data.get('notes', ''),
                performed_by=request.user
            )

            return Response({
                'message': _('Stock added.'),
                'new_quantity': item.quantity,
                'available': item.available_quantity,
            })

        except (ValueError, TypeError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_stock(self, request, pk=None):
        """کاهش موجودی"""
        item = self.get_object()
        quantity = request.data.get('quantity', 0)

        try:
            qty = int(quantity)
            if qty <= 0:
                raise ValueError('Quantity must be positive')

            item.remove_stock(qty)

            # ثبت حرکت
            StockMovement.objects.create(
                inventory_item=item,
                movement_type='out',
                quantity=qty,
                from_warehouse=item.warehouse,
                reference=request.data.get('reference', ''),
                notes=request.data.get('notes', ''),
                performed_by=request.user
            )

            return Response({
                'message': _('Stock removed.'),
                'new_quantity': item.quantity,
                'available': item.available_quantity,
            })

        except (ValueError, TypeError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """انتقال موجودی به انبار دیگر"""
        item = self.get_object()
        serializer = StockTransferSerializer(data={
            'inventory_item_id': str(item.id),
            'to_warehouse_id': request.data.get('to_warehouse'),
            'quantity': request.data.get('quantity'),
            'notes': request.data.get('notes', ''),
        })
        serializer.is_valid(raise_exception=True)

        try:
            to_warehouse = serializer.validated_data['to_warehouse']
            qty = serializer.validated_data['quantity']

            # کم کردن از مبدا
            item.remove_stock(qty)

            # اضافه کردن به مقصد
            target_item, created = InventoryItem.objects.get_or_create(
                warehouse=to_warehouse,
                product=item.product,
                batch_number=item.batch_number,
                defaults={
                    'quantity': qty,
                    'shelf': item.shelf,
                    'status': 'in_stock',
                }
            )

            if not created:
                target_item.add_stock(qty)

            # ثبت حرکت
            StockMovement.objects.create(
                inventory_item=item,
                movement_type='transfer',
                quantity=qty,
                from_warehouse=item.warehouse,
                to_warehouse=to_warehouse,
                reference=f"TRF-{item.id}-{to_warehouse.id}",
                notes=serializer.validated_data.get('notes', ''),
                performed_by=request.user
            )

            logger.info(f"Stock transferred: {item.product.sku} x{qty} from {item.warehouse.code} to {to_warehouse.code}")

            return Response({
                'message': _('Transfer successful.'),
                'source_quantity': item.quantity,
                'target_quantity': target_item.quantity,
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """تاریخچه جابجایی‌های یک موجودی"""
        item = self.get_object()
        movements = item.movements.all()

        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = StockMovementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)


class StockMovementViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """
    ViewSet مشاهده جابجایی‌های موجودی (فقط خواندنی)
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated, IsWarehouseStaff]

    def get_queryset(self):
        queryset = StockMovement.objects.select_related(
            'inventory_item', 'inventory_item__product',
            'inventory_item__warehouse', 'from_warehouse',
            'to_warehouse', 'performed_by'
        )

        # فیلترها
        item = self.request.query_params.get('item')
        if item:
            queryset = queryset.filter(inventory_item_id=item)

        movement_type = self.request.query_params.get('type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        warehouse = self.request.query_params.get('warehouse')
        if warehouse:
            queryset = queryset.filter(
                db_models.Q(from_warehouse_id=warehouse) |
                db_models.Q(to_warehouse_id=warehouse)
            )

        return queryset