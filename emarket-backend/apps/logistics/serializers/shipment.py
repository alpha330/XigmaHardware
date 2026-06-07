from decimal import Decimal
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.logistics.models import Shipment, ShipmentTracking, Courier
from apps.logistics.enums import ShipmentStatus, CourierType
from apps.logistics.serializers.courier import CourierSerializer
from apps.logistics.serializers.address import UserAddressSerializer


class ShipmentTrackingSerializer(serializers.ModelSerializer):
    """سریالایزر رویداد رهگیری"""
    status_display = serializers.SerializerMethodField()
    location_display = serializers.SerializerMethodField()
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = ShipmentTracking
        fields = [
            'id', 'status', 'status_display', 'description',
            'location_latitude', 'location_longitude', 'location_display',
            'created_by', 'created_at', 'created_at_display',
        ]

    def get_status_display(self, obj):
        icons = {
            'pending': '⏳', 'assigned': '🚀', 'picked_up': '📦',
            'in_transit': '🛵', 'delivered': '✅',
            'returned': '↩️', 'cancelled': '❌',
        }
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
            'icon': icons.get(obj.status, '📍'),
            'step': {
                'pending': 1, 'assigned': 2, 'picked_up': 3,
                'in_transit': 4, 'delivered': 5,
            }.get(obj.status, 0),
        }

    def get_location_display(self, obj):
        if obj.location_latitude and obj.location_longitude:
            return {
                'lat': float(obj.location_latitude),
                'lng': float(obj.location_longitude),
                'url': f"https://maps.google.com/?q={obj.location_latitude},{obj.location_longitude}",
            }
        return None

    def get_created_at_display(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 0:
            return f'{diff.days} days ago'
        elif diff.seconds > 3600:
            return f'{diff.seconds // 3600} hours ago'
        elif diff.seconds > 60:
            return f'{diff.seconds // 60} minutes ago'
        return 'Just now'


class ShipmentSerializer(serializers.ModelSerializer):
    """سریالایزر کامل محموله"""
    tracking_events = ShipmentTrackingSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    courier = CourierSerializer(read_only=True)
    destination_address = UserAddressSerializer(read_only=True)
    progress_percent = serializers.SerializerMethodField()
    created_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            'id', 'user', 'customer_name', 'invoice',
            'origin_warehouse', 'origin_address',
            'origin_latitude', 'origin_longitude',
            'destination_address', 'destination_latitude', 'destination_longitude',
            'courier', 'courier_tracking_code',
            'status', 'status_display', 'progress_percent',
            'shipping_cost', 'courier_cost', 'customer_cost',
            'distance_km', 'estimated_duration',
            'package_weight_kg', 'package_description',
            'notes', 'courier_notes',
            'tracking_events',
            'assigned_at', 'picked_up_at', 'delivered_at',
            'created_at', 'created_at_jalali', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at',
            'assigned_at', 'picked_up_at', 'delivered_at',
        ]

    def get_status_display(self, obj):
        colors = {
            'pending': '#ffc107', 'assigned': '#17a2b8',
            'picked_up': '#6f42c1', 'in_transit': '#0d6efd',
            'delivered': '#28a745', 'returned': '#dc3545', 'cancelled': '#6c757d',
        }
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
            'color': colors.get(obj.status, '#6c757d'),
            'step': {
                'pending': 1, 'assigned': 2, 'picked_up': 3,
                'in_transit': 4, 'delivered': 5,
            }.get(obj.status, 0),
        }

    def get_customer_name(self, obj):
        return obj.user.get_display_name() if obj.user else '-'

    def get_progress_percent(self, obj):
        """درصد پیشرفت"""
        progress = {
            'pending': 10, 'assigned': 25, 'picked_up': 50,
            'in_transit': 75, 'delivered': 100,
        }
        return progress.get(obj.status, 0)

    def get_created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return None


class ShipmentCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد محموله"""

    class Meta:
        model = Shipment
        fields = [
            'invoice', 'origin_warehouse', 'destination_address',
            'courier', 'package_description', 'package_weight_kg',
            'notes',
        ]

    def validate(self, data):
        """اعتبارسنجی"""
        origin = data.get('origin_warehouse')
        dest = data.get('destination_address')

        if origin and dest:
            # چک کن مبدا و مقصد یکی نباشن
            if hasattr(origin, 'latitude') and hasattr(dest, 'latitude'):
                if origin.latitude and dest.latitude:
                    if abs(float(origin.latitude) - float(dest.latitude)) < 0.0001:
                        if abs(float(origin.longitude) - float(dest.longitude)) < 0.0001:
                            raise serializers.ValidationError(
                                _('Origin and destination cannot be the same.')
                            )

        return data


class ShipmentStatusUpdateSerializer(serializers.Serializer):
    """سریالایزر بروزرسانی وضعیت"""
    status = serializers.ChoiceField(choices=ShipmentStatus.choices, required=True)
    description = serializers.CharField(required=False, allow_blank=True, max_length=500)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False)

    def validate_status(self, value):
        shipment = self.context.get('shipment')
        if shipment:
            # اعتبارسنجی تغییر وضعیت
            valid_transitions = {
                'pending': ['assigned', 'cancelled'],
                'assigned': ['picked_up', 'cancelled'],
                'picked_up': ['in_transit', 'cancelled'],
                'in_transit': ['delivered', 'cancelled'],
                'delivered': [],
                'cancelled': [],
                'returned': [],
            }

            current = shipment.status
            if current in valid_transitions and value not in valid_transitions[current]:
                raise serializers.ValidationError(
                    _(f'Cannot change from {current} to {value}.')
                )

        return value


class ShipmentAssignSerializer(serializers.Serializer):
    """سریالایزر تخصیص پیک"""
    courier_id = serializers.UUIDField(required=True)

    def validate_courier_id(self, value):
        try:
            courier = Courier.objects.get(
                id=value, is_active=True, is_available=True
            )
            self.context['courier'] = courier
        except Courier.DoesNotExist:
            raise serializers.ValidationError(_('Courier not found or not available.'))
        return value


class ShipmentCostEstimateSerializer(serializers.Serializer):
    """سریالایزر استعلام هزینه ارسال"""
    origin_lat = serializers.DecimalField(max_digits=10, decimal_places=7, required=True)
    origin_lng = serializers.DecimalField(max_digits=10, decimal_places=7, required=True)
    dest_lat = serializers.DecimalField(max_digits=10, decimal_places=7, required=True)
    dest_lng = serializers.DecimalField(max_digits=10, decimal_places=7, required=True)
    vehicle_type = serializers.ChoiceField(
        choices=[('motorcycle', 'Motorcycle'), ('car', 'Car'), ('pickup', 'Pickup'),
                 ('van', 'Van'), ('truck', 'Truck')],
        default='motorcycle'
    )
    package_weight_kg = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    is_fragile = serializers.BooleanField(default=False)
    is_express = serializers.BooleanField(default=False)