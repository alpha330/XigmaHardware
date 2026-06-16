from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.stock.models import Warehouse
from apps.accounts.serializers.user import UserListSerializer


class WarehouseListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست انبارها"""
    warehouse_type_display = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    sub_warehouses_count = serializers.IntegerField(read_only=True)
    location = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name', 'warehouse_type', 'warehouse_type_display',
            'scope', 'manager_name', 'sub_warehouses_count',
            'location', 'is_active', 'current_items', 'capacity',
            'created_at',
        ]

    def get_warehouse_type_display(self, obj):
        return {
            'code': obj.warehouse_type,
            'label': obj.get_warehouse_type_display(),
            'icon': {
                'main': '🏭',
                'sub': '📦',
                'specialized': '🔧',
                'temporary': '⏳',
            }.get(obj.warehouse_type, '📦')
        }

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.get_display_name()
        return None

    def get_location(self, obj):
        if obj.latitude and obj.longitude:
            return {
                'lat': float(obj.latitude),
                'lng': float(obj.longitude),
            }
        return None


class WarehouseSerializer(serializers.ModelSerializer):
    """سریالایزر کامل انبار"""
    warehouse_type_display = serializers.SerializerMethodField()

    # 🎯 این دو فیلد برای "خواندن" (GET) هستند و شی کامل را برمی‌گردانند
    manager_info = UserListSerializer(source='manager', read_only=True)
    staff_info = UserListSerializer(source='staff', many=True, read_only=True)

    # 🎯 فیلدهای manager و staff اصلی (که از نوع PrimaryKeyRelatedField هستند) برای "نوشتن" (PATCH/PUT/POST) استفاده می‌شوند

    sub_warehouses = serializers.SerializerMethodField()
    parent_info = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    utilization = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name', 'warehouse_type', 'warehouse_type_display',
            'scope', 'parent', 'parent_info', 'sub_warehouses',
            'address', 'latitude', 'longitude', 'location',
            'phone', 'email',

            'manager', 'manager_info', # هر دو را اضافه کنید
            'staff', 'staff_info',     # هر دو را اضافه کنید

            'capacity', 'current_items', 'utilization',
            'specialized_hardware', 'description',
            'is_active', 'is_public',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] # code را از اینجا برداشتم تا قابل آپدیت باشد (اگر می‌خواهید غیرقابل آپدیت باشد، برش گردانید)

    def get_warehouse_type_display(self, obj):
        return {
            'code': obj.warehouse_type,
            'label': obj.get_warehouse_type_display(),
        }

    def get_sub_warehouses(self, obj):
        if obj.sub_warehouses.exists():
            return WarehouseListSerializer(
                obj.sub_warehouses.all()[:10],
                many=True
            ).data
        return []

    def get_parent_info(self, obj):
        if obj.parent:
            return {
                'id': str(obj.parent.id),
                'code': obj.parent.code,
                'name': obj.parent.name,
            }
        return None

    def get_location(self, obj):
        if obj.latitude and obj.longitude:
            return {
                'lat': float(obj.latitude),
                'lng': float(obj.longitude),
                'map_url': f"https://maps.google.com/?q={obj.latitude},{obj.longitude}",
            }
        return None

    def get_utilization(self, obj):
        if obj.capacity > 0:
            percent = (obj.current_items / obj.capacity) * 100
            return {
                'percent': round(percent, 1),
                'current': obj.current_items,
                'max': obj.capacity,
                'status': 'critical' if percent > 90 else 'warning' if percent > 70 else 'ok'
            }
        return None


class WarehouseCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد انبار"""

    class Meta:
        model = Warehouse
        fields = [
            'name', 'code', 'warehouse_type', 'scope',
            'parent', 'address', 'latitude', 'longitude',
            'phone', 'email', 'manager',
            'capacity', 'specialized_hardware',
            'description', 'is_active', 'is_public',
        ]

    def validate_code(self, value):
        """بررسی یکتایی کد"""
        if Warehouse.objects.filter(code=value).exists():
            raise serializers.ValidationError(_('This warehouse code already exists.'))
        return value.upper()

    def validate(self, data):
        """اعتبارسنجی منطقی"""
        warehouse_type = data.get('warehouse_type')
        parent = data.get('parent')
        scope = data.get('scope')
        specialized = data.get('specialized_hardware')

        # انبار فرعی باید parent داشته باشه
        if warehouse_type == 'sub' and not parent:
            raise serializers.ValidationError({
                'parent': _('Sub warehouse must have a parent warehouse.')
            })

        # انبار اصلی نباید parent داشته باشه
        if warehouse_type == 'main' and parent:
            raise serializers.ValidationError({
                'parent': _('Main warehouse cannot have a parent.')
            })

        # انبار تخصصی باید specialized_hardware رو مشخص کنه
        if scope == 'specialized' and not specialized:
            raise serializers.ValidationError({
                'specialized_hardware': _('Specialized warehouse must specify hardware type.')
            })

        return data