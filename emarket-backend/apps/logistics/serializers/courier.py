from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.logistics.models import Courier
from apps.logistics.enums import CourierType


class CourierSerializer(serializers.ModelSerializer):
    """سریالایزر پیک"""
    success_rate = serializers.FloatField(read_only=True)
    courier_type_display = serializers.SerializerMethodField()
    vehicle_type_display = serializers.SerializerMethodField()
    active_shipments_count = serializers.SerializerMethodField()

    class Meta:
        model = Courier
        fields = [
            'id', 'courier_type', 'courier_type_display',
            'name', 'phone', 'email',
            'vehicle_type', 'vehicle_type_display', 'vehicle_plate',
            'is_active', 'is_available',
            'current_latitude', 'current_longitude', 'location_updated_at',
            'rating', 'total_deliveries', 'successful_deliveries', 'success_rate',
            'active_shipments_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'rating', 'total_deliveries', 'successful_deliveries',
            'created_at', 'updated_at',
        ]

    def get_courier_type_display(self, obj):
        icons = {
            'internal': '🛵', 'alopeyk': '🟢',
            'snappbox': '🟣', 'post': '📮', 'tipax': '📦',
        }
        return {
            'code': obj.courier_type,
            'label': obj.get_courier_type_display(),
            'icon': icons.get(obj.courier_type, '🛵'),
            'is_external': obj.courier_type != CourierType.INTERNAL,
        }

    def get_vehicle_type_display(self, obj):
        icons = {
            'motorcycle': '🏍️', 'car': '🚗', 'pickup': '🛻',
            'van': '🚐', 'truck': '🚛',
        }
        return {
            'code': obj.vehicle_type,
            'label': obj.get_vehicle_type_display(),
            'icon': icons.get(obj.vehicle_type, '🛵'),
        }

    def get_active_shipments_count(self, obj):
        from apps.logistics.enums import ShipmentStatus
        return obj.shipments.filter(
            status__in=[
                ShipmentStatus.ASSIGNED,
                ShipmentStatus.PICKED_UP,
                ShipmentStatus.IN_TRANSIT,
            ]
        ).count()


class CourierCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد پیک"""

    class Meta:
        model = Courier
        fields = [
            'courier_type', 'name', 'phone', 'email',
            'vehicle_type', 'vehicle_plate',
            'user', 'national_code',
            'api_key', 'api_secret', 'extra_config',
            'is_active',
        ]

    def validate_phone(self, value):
        if value and len(value) != 11:
            raise serializers.ValidationError(_('Phone must be 11 digits.'))
        return value


class CourierLocationSerializer(serializers.Serializer):
    """سریالایزر بروزرسانی موقعیت پیک"""
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=True)

    def validate_latitude(self, value):
        if not -90 <= float(value) <= 90:
            raise serializers.ValidationError(_('Invalid latitude.'))
        return value

    def validate_longitude(self, value):
        if not -180 <= float(value) <= 180:
            raise serializers.ValidationError(_('Invalid longitude.'))
        return value