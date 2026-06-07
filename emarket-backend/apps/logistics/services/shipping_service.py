"""
سرویس مدیریت ارسال و محاسبه هزینه
"""

import logging
from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.logistics.models import Shipment, ShipmentTracking, Courier
from apps.logistics.enums import ShipmentStatus, CourierType
from math import radians, sin, cos, sqrt, atan2

logger = logging.getLogger(__name__)


class ShippingService:
    """
    سرویس مدیریت ارسال‌ها

    عملیات:
    - محاسبه هزینه ارسال
    - محاسبه مسافت
    - ایجاد محموله
    - تخصیص پیک
    - بروزرسانی وضعیت
    - رهگیری
    """

    # تعرفه‌های پایه (قابل تنظیم توسط ادمین)
    BASE_RATES = {
        'motorcycle': {
            'base_fee': Decimal('25000'),      # هزینه پایه (ریال)
            'per_km': Decimal('5000'),         # هزینه هر کیلومتر
            'min_fee': Decimal('30000'),       # حداقل هزینه
            'max_distance_km': 15,             # حداکثر مسافت
        },
        'car': {
            'base_fee': Decimal('50000'),
            'per_km': Decimal('8000'),
            'min_fee': Decimal('60000'),
            'max_distance_km': 50,
        },
        'pickup': {
            'base_fee': Decimal('80000'),
            'per_km': Decimal('10000'),
            'min_fee': Decimal('100000'),
            'max_distance_km': 100,
        },
        'van': {
            'base_fee': Decimal('120000'),
            'per_km': Decimal('15000'),
            'min_fee': Decimal('150000'),
            'max_distance_km': 200,
        },
        'truck': {
            'base_fee': Decimal('200000'),
            'per_km': Decimal('20000'),
            'min_fee': Decimal('250000'),
            'max_distance_km': 500,
        },
    }

    # ضریب‌های اضافی
    SURCHARGE_FACTORS = {
        'heavy_package': Decimal('1.3'),      # بسته سنگین (>20kg)
        'fragile': Decimal('1.2'),            # شکستنی
        'express': Decimal('1.5'),             # ارسال فوری
        'rush_hour': Decimal('1.2'),           # ساعت شلوغی
        'weekend': Decimal('1.1'),             # آخر هفته
    }

    # ==================== Distance Calculation ====================

    @classmethod
    def calculate_distance_km(cls, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        محاسبه مسافت با فرمول Haversine

        Args:
            lat1, lng1: مختصات مبدا
            lat2, lng2: مختصات مقصد

        Returns:
            float: مسافت به کیلومتر
        """
        R = 6371  # شعاع زمین به کیلومتر

        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        return round(distance, 2)

    # ==================== Cost Calculation ====================

    @classmethod
    def calculate_shipping_cost(
        cls,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        vehicle_type: str = 'motorcycle',
        package_weight_kg: float = None,
        is_fragile: bool = False,
        is_express: bool = False,
    ) -> dict:
        """
        محاسبه هزینه ارسال

        Args:
            origin_lat, origin_lng: مبدا
            dest_lat, dest_lng: مقصد
            vehicle_type: نوع وسیله
            package_weight_kg: وزن بسته
            is_fragile: شکستنی
            is_express: فوری

        Returns:
            dict
        """
        # محاسبه مسافت
        distance = cls.calculate_distance_km(origin_lat, origin_lng, dest_lat, dest_lng)

        # دریافت تعرفه
        rates = cls.BASE_RATES.get(vehicle_type, cls.BASE_RATES['motorcycle'])

        # چک حداکثر مسافت
        if distance > rates['max_distance_km']:
            return {
                'success': False,
                'error': _(f'Distance {distance:.1f}km exceeds maximum {rates["max_distance_km"]}km for {vehicle_type}.'),
                'distance_km': distance,
            }

        # محاسبه هزینه پایه
        base_cost = rates['base_fee'] + (rates['per_km'] * Decimal(str(distance)))

        # حداقل هزینه
        base_cost = max(base_cost, rates['min_fee'])

        # محاسبه هزینه اضافی
        surcharge = Decimal('1.0')
        surcharge_details = []

        # بسته سنگین
        if package_weight_kg and package_weight_kg > 20:
            surcharge *= cls.SURCHARGE_FACTORS['heavy_package']
            surcharge_details.append({
                'reason': 'heavy_package',
                'factor': float(cls.SURCHARGE_FACTORS['heavy_package']),
                'label': _('Heavy Package (>20kg)'),
            })

        # شکستنی
        if is_fragile:
            surcharge *= cls.SURCHARGE_FACTORS['fragile']
            surcharge_details.append({
                'reason': 'fragile',
                'factor': float(cls.SURCHARGE_FACTORS['fragile']),
                'label': _('Fragile Item'),
            })

        # فوری
        if is_express:
            surcharge *= cls.SURCHARGE_FACTORS['express']
            surcharge_details.append({
                'reason': 'express',
                'factor': float(cls.SURCHARGE_FACTORS['express']),
                'label': _('Express Delivery'),
            })

        # ساعت شلوغی (۸-۱۰ صبح و ۴-۸ عصر)
        now = timezone.now()
        if (8 <= now.hour <= 10) or (16 <= now.hour <= 20):
            surcharge *= cls.SURCHARGE_FACTORS['rush_hour']
            surcharge_details.append({
                'reason': 'rush_hour',
                'factor': float(cls.SURCHARGE_FACTORS['rush_hour']),
                'label': _('Rush Hour'),
            })

        # آخر هفته (پنجشنبه و جمعه)
        if now.weekday() in [3, 4]:  # Iranian weekend
            surcharge *= cls.SURCHARGE_FACTORS['weekend']
            surcharge_details.append({
                'reason': 'weekend',
                'factor': float(cls.SURCHARGE_FACTORS['weekend']),
                'label': _('Weekend'),
            })

        # هزینه نهایی
        total_cost = base_cost * surcharge

        # تخمین زمان (حدود ۵ دقیقه به ازای هر کیلومتر + ۱۰ دقیقه پایه)
        estimated_minutes = int(distance * 5 + 10)

        return {
            'success': True,
            'distance_km': distance,
            'base_cost': float(base_cost),
            'surcharge_factor': float(surcharge),
            'surcharge_details': surcharge_details,
            'total_cost': float(total_cost),
            'estimated_minutes': estimated_minutes,
            'vehicle_type': vehicle_type,
            'currency': 'IRR',
        }

    @classmethod
    def calculate_shipment_cost(cls, shipment: Shipment) -> dict:
        """
        محاسبه هزینه برای یک محموله

        Args:
            shipment: محموله

        Returns:
            dict
        """
        # مختصات مبدا
        origin_lat = float(shipment.origin_latitude) if shipment.origin_latitude else 0
        origin_lng = float(shipment.origin_longitude) if shipment.origin_longitude else 0

        # مختصات مقصد
        if shipment.destination_address:
            dest_lat = float(shipment.destination_address.latitude)
            dest_lng = float(shipment.destination_address.longitude)
        else:
            dest_lat = float(shipment.destination_latitude or 0)
            dest_lng = float(shipment.destination_longitude or 0)

        vehicle = 'motorcycle'
        if shipment.courier:
            vehicle = shipment.courier.vehicle_type

        return cls.calculate_shipping_cost(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            vehicle_type=vehicle,
            package_weight_kg=float(shipment.package_weight_kg) if shipment.package_weight_kg else None,
        )

    # ==================== Shipment Management ====================

    @classmethod
    @db_transaction.atomic
    def create_shipment(
        cls,
        user,
        invoice=None,
        origin_warehouse=None,
        destination_address=None,
        courier=None,
        package_description='',
        package_weight_kg=None,
        notes='',
    ) -> Shipment:
        """
        ایجاد محموله جدید

        Args:
            user: کاربر
            invoice: فاکتور
            origin_warehouse: انبار مبدا
            destination_address: آدرس مقصد
            courier: پیک
            package_description: توضیحات بسته
            package_weight_kg: وزن
            notes: یادداشت

        Returns:
            Shipment
        """
        shipment = Shipment.objects.create(
            user=user,
            invoice=invoice,
            origin_warehouse=origin_warehouse,
            destination_address=destination_address,
            courier=courier,
            package_description=package_description,
            package_weight_kg=package_weight_kg,
            notes=notes,
            status=ShipmentStatus.PENDING,
        )

        # تنظیم مختصات مبدا از انبار
        if origin_warehouse:
            shipment.origin_latitude = origin_warehouse.latitude
            shipment.origin_longitude = origin_warehouse.longitude
            shipment.origin_address = origin_warehouse.full_address

        # تنظیم مختصات مقصد از آدرس
        if destination_address:
            shipment.destination_latitude = destination_address.latitude
            shipment.destination_longitude = destination_address.longitude

        # محاسبه هزینه
        cost = cls.calculate_shipment_cost(shipment)
        if cost['success']:
            shipment.distance_km = Decimal(str(cost['distance_km']))
            shipment.estimated_duration = cost['estimated_minutes']
            shipment.customer_cost = Decimal(str(cost['total_cost']))

        shipment.save()

        # ثبت رویداد اولیه
        ShipmentTracking.objects.create(
            shipment=shipment,
            status=ShipmentStatus.PENDING,
            description=_('Shipment created'),
        )

        logger.info(
            f"Shipment created: {shipment.id} for user {user.email or user.mobile}"
        )

        return shipment

    @classmethod
    @db_transaction.atomic
    def assign_courier(cls, shipment: Shipment, courier: Courier) -> Shipment:
        """
        تخصیص پیک به محموله

        Args:
            shipment: محموله
            courier: پیک

        Returns:
            Shipment
        """
        if shipment.status not in [ShipmentStatus.PENDING]:
            raise ValueError(_('Can only assign courier to pending shipments.'))

        shipment.assign_courier(courier)

        # محاسبه مجدد هزینه با نوع وسیله پیک
        cost = cls.calculate_shipment_cost(shipment)
        if cost['success']:
            shipment.customer_cost = Decimal(str(cost['total_cost']))
            shipment.distance_km = Decimal(str(cost['distance_km']))
            shipment.estimated_duration = cost['estimated_minutes']
            shipment.save()

        # ثبت رویداد
        ShipmentTracking.objects.create(
            shipment=shipment,
            status=ShipmentStatus.ASSIGNED,
            description=_(f'Assigned to {courier.name}'),
        )

        logger.info(f"Courier {courier.name} assigned to shipment {shipment.id}")

        # اگر پیک خارجی هست، سفارش رو توی API ثبت کن
        if courier.courier_type != CourierType.INTERNAL:
            try:
                from apps.logistics.services.courier_service import CourierService
                result = CourierService.create_external_order(courier, shipment)

                if result.get('success'):
                    shipment.courier_tracking_code = result.get('tracking_code', '')
                    shipment.save()
                else:
                    logger.error(f"External order failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"External order error: {str(e)}")

        return shipment

    @classmethod
    @db_transaction.atomic
    def update_shipment_status(
        cls,
        shipment: Shipment,
        status: str,
        description: str = '',
        latitude: float = None,
        longitude: float = None,
        updated_by=None,
    ) -> Shipment:
        """
        بروزرسانی وضعیت محموله

        Args:
            shipment: محموله
            status: وضعیت جدید
            description: توضیحات
            latitude, longitude: موقعیت فعلی
            updated_by: بروزرسانی کننده

        Returns:
            Shipment
        """
        old_status = shipment.status

        if status == ShipmentStatus.PICKED_UP:
            shipment.mark_picked_up()
        elif status == ShipmentStatus.DELIVERED:
            shipment.mark_delivered()
        elif status == ShipmentStatus.CANCELLED:
            shipment.cancel()
        elif status == ShipmentStatus.IN_TRANSIT:
            shipment.status = ShipmentStatus.IN_TRANSIT
            shipment.save()
        else:
            shipment.status = status
            shipment.save()

        # ثبت رویداد رهگیری
        ShipmentTracking.objects.create(
            shipment=shipment,
            status=status,
            description=description,
            location_latitude=latitude,
            location_longitude=longitude,
            created_by=updated_by,
        )

        logger.info(
            f"Shipment {shipment.id} status: {old_status} -> {status}"
        )

        return shipment

    @classmethod
    def get_shipment_tracking(cls, shipment: Shipment) -> dict:
        """
        دریافت اطلاعات رهگیری

        Args:
            shipment: محموله

        Returns:
            dict
        """
        events = shipment.tracking_events.all()

        # اطلاعات پیک (اگر داخلی باشه)
        courier_info = None
        if shipment.courier and shipment.courier.courier_type == CourierType.INTERNAL:
            courier_info = {
                'name': shipment.courier.name,
                'phone': shipment.courier.phone,
                'current_lat': float(shipment.courier.current_latitude) if shipment.courier.current_latitude else None,
                'current_lng': float(shipment.courier.current_longitude) if shipment.courier.current_longitude else None,
                'location_updated': shipment.courier.location_updated_at.isoformat() if shipment.courier.location_updated_at else None,
            }

        return {
            'shipment_id': str(shipment.id),
            'status': shipment.status,
            'status_display': shipment.get_status_display(),
            'courier': courier_info,
            'courier_tracking_code': shipment.courier_tracking_code,
            'estimated_delivery': shipment.delivered_at.isoformat() if shipment.delivered_at else None,
            'events': [
                {
                    'status': e.status,
                    'status_display': e.get_status_display(),
                    'description': e.description,
                    'location': {
                        'lat': float(e.location_latitude) if e.location_latitude else None,
                        'lng': float(e.location_longitude) if e.location_longitude else None,
                    },
                    'created_at': e.created_at.isoformat(),
                }
                for e in events
            ],
        }

    @classmethod
    def get_active_shipments_for_courier(cls, courier: Courier):
        """
        محموله‌های فعال یک پیک

        Args:
            courier: پیک

        Returns:
            QuerySet
        """
        return Shipment.objects.filter(
            courier=courier,
            status__in=[
                ShipmentStatus.ASSIGNED,
                ShipmentStatus.PICKED_UP,
                ShipmentStatus.IN_TRANSIT,
            ]
        ).order_by('-created_at')

    @classmethod
    def get_user_shipments(cls, user):
        """
        محموله‌های یک کاربر

        Args:
            user: کاربر

        Returns:
            QuerySet
        """
        return Shipment.objects.filter(user=user).order_by('-created_at')

    @classmethod
    def find_nearest_available_couriers(cls, latitude: float, longitude: float, limit: int = 5):
        """
        پیدا کردن نزدیک‌ترین پیک‌های آماده

        Args:
            latitude, longitude: موقعیت
            limit: تعداد

        Returns:
            list
        """
        couriers = Courier.objects.filter(
            is_active=True,
            is_available=True,
            courier_type=CourierType.INTERNAL,
            current_latitude__isnull=False,
            current_longitude__isnull=False,
        )

        # محاسبه مسافت و مرتب‌سازی
        courier_distances = []
        for courier in couriers:
            distance = cls.calculate_distance_km(
                latitude, longitude,
                float(courier.current_latitude),
                float(courier.current_longitude),
            )
            courier_distances.append({
                'courier': courier,
                'distance_km': distance,
            })

        # مرتب‌سازی بر اساس مسافت
        courier_distances.sort(key=lambda x: x['distance_km'])

        return courier_distances[:limit]