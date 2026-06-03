from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.stock.models import InventoryItem, StockMovement
from apps.stock.enums import InventoryStatus


class InventoryItemSerializer(serializers.ModelSerializer):
    """سریالایزر موجودی انبار"""
    warehouse_name = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    available_quantity = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    location = serializers.CharField(read_only=True)
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'warehouse', 'warehouse_name', 'product', 'product_sku',
            'product_name', 'quantity', 'reserved_quantity', 'available_quantity',
            'minimum_quantity', 'is_low_stock',
            'shelf', 'aisle', 'section', 'location', 'location_barcode',
            'status', 'status_display',
            'batch_number', 'received_date', 'expiry_date',
            'notes', 'last_checked_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_warehouse_name(self, obj):
        return f"{obj.warehouse.code} - {obj.warehouse.name}"

    def get_product_sku(self, obj):
        return obj.product.sku

    def get_product_name(self, obj):
        return obj.product.name

    def get_status_display(self, obj):
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
            'color': {
                'in_stock': 'green',
                'reserved': 'blue',
                'in_transit': 'yellow',
                'damaged': 'red',
                'returned': 'orange',
            }.get(obj.status, 'gray')
        }


class InventoryCreateSerializer(serializers.ModelSerializer):
    """سریالایزر افزودن موجودی به انبار"""

    class Meta:
        model = InventoryItem
        fields = [
            'warehouse', 'product', 'quantity',
            'shelf', 'aisle', 'section',
            'batch_number', 'received_date', 'expiry_date',
            'notes',
        ]

    def validate(self, data):
        warehouse = data.get('warehouse')
        product = data.get('product')

        # بررسی تکراری نبودن
        if InventoryItem.objects.filter(
            warehouse=warehouse,
            product=product,
            batch_number=data.get('batch_number', '')
        ).exists():
            raise serializers.ValidationError(
                _('This product already exists in this warehouse. Use update instead.')
            )

        return data


class StockMovementSerializer(serializers.ModelSerializer):
    """سریالایزر جابجایی موجودی"""
    movement_type_display = serializers.SerializerMethodField()
    performed_by_name = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = [
            'id', 'inventory_item', 'product_info',
            'movement_type', 'movement_type_display',
            'quantity', 'from_warehouse', 'to_warehouse',
            'reference', 'notes', 'performed_by', 'performed_by_name',
            'created_at',
        ]
        read_only_fields = ['id', 'performed_by', 'created_at']

    def get_movement_type_display(self, obj):
        return {
            'code': obj.movement_type,
            'label': obj.get_movement_type_display(),
            'is_inbound': obj.movement_type in ['in', 'return', 'unreserve'],
            'is_outbound': obj.movement_type in ['out', 'reserve', 'damaged'],
        }

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_display_name()
        return None

    def get_product_info(self, obj):
        return {
            'sku': obj.inventory_item.product.sku,
            'name': obj.inventory_item.product.name,
            'warehouse': obj.inventory_item.warehouse.code,
        }


class StockTransferSerializer(serializers.Serializer):
    """سریالایزر انتقال بین انبارها"""
    inventory_item_id = serializers.UUIDField()
    to_warehouse_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        from apps.stock.models import InventoryItem, Warehouse

        try:
            item = InventoryItem.objects.get(id=data['inventory_item_id'])
        except InventoryItem.DoesNotExist:
            raise serializers.ValidationError({'inventory_item_id': _('Item not found.')})

        try:
            to_warehouse = Warehouse.objects.get(id=data['to_warehouse_id'])
        except Warehouse.DoesNotExist:
            raise serializers.ValidationError({'to_warehouse_id': _('Warehouse not found.')})

        if item.warehouse == to_warehouse:
            raise serializers.ValidationError(
                _('Source and destination warehouses must be different.')
            )

        if data['quantity'] > item.available_quantity:
            raise serializers.ValidationError({
                'quantity': _(f'Not enough stock. Available: {item.available_quantity}')
            })

        data['inventory_item'] = item
        data['to_warehouse'] = to_warehouse
        return data