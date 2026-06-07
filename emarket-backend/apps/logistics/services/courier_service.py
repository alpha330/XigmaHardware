"""
سرویس مدیریت پیک‌ها و ارتباط با API های خارجی
"""

import logging
from django.utils.translation import gettext_lazy as _
from apps.logistics.models import Courier
from apps.logistics.enums import CourierType
from apps.logistics.integrations import AlopeykAPI, SnappBoxAPI

logger = logging.getLogger(__name__)


class CourierService:
    """
    سرویس یکپارچه مدیریت پیک

    عملیات:
    - انتخاب بهترین پیک
    - استعلام قیمت از همه سرویس‌ها
    - ثبت سفارش در سرویس خارجی
    - پیگیری وضعیت
    """

    API_CLASSES = {
        CourierType.ALOPEYK: AlopeykAPI,
        CourierType.SNAPPBOX: SnappBoxAPI,
    }

    @classmethod
    def get_api_instance(cls, courier: Courier):
        """
        دریافت نمونه API برای پیک

        Args:
            courier: مدل پیک

        Returns:
            BaseCourierAPI or None
        """
        if courier.courier_type == CourierType.INTERNAL:
            return None  # پیک داخلی API نداره

        api_class = cls.API_CLASSES.get(courier.courier_type)

        if not api_class:
            raise ValueError(f"No API for courier type: {courier.courier_type}")

        return api_class(
            api_key=courier.api_key,
            api_secret=courier.api_secret,
            is_sandbox=courier.extra_config.get('sandbox', False),
        )

    @classmethod
    def get_price_estimates(
        cls,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        package_weight: float = None,
    ) -> dict:
        """
        استعلام قیمت از همه پیک‌های فعال

        Returns:
            {
                'internal': {...},
                'alopeyk': {...},
                'snappbox': {...},
                'best': {...},
            }
        """
        results = {}

        active_couriers = Courier.objects.filter(
            is_active=True,
        ).exclude(courier_type=CourierType.INTERNAL)

        for courier in active_couriers:
            try:
                api = cls.get_api_instance(courier)
                if api:
                    estimate = api.get_price_estimate(
                        origin_lat=origin_lat,
                        origin_lng=origin_lng,
                        dest_lat=dest_lat,
                        dest_lng=dest_lng,
                        vehicle_type=courier.vehicle_type,
                        package_weight=package_weight,
                    )
                    results[courier.courier_type] = {
                        'courier_id': str(courier.id),
                        'courier_name': courier.name,
                        **estimate,
                    }
            except Exception as e:
                logger.error(f"Estimate failed for {courier.name}: {str(e)}")
                results[courier.courier_type] = {
                    'success': False,
                    'error': str(e),
                }

        # پیدا کردن بهترین قیمت
        best = None
        best_price = float('inf')

        for key, result in results.items():
            if result.get('success') and result.get('price', float('inf')) < best_price:
                best_price = result['price']
                best = result
                best['type'] = key

        results['best'] = best

        return results

    @classmethod
    def create_external_order(cls, courier: Courier, shipment) -> dict:
        """
        ثبت سفارش در سرویس خارجی

        Args:
            courier: پیک
            shipment: محموله

        Returns:
            dict
        """
        api = cls.get_api_instance(courier)

        if not api:
            return {'success': False, 'error': 'Internal courier - no API needed.'}

        # آدرس مقصد
        dest = shipment.destination_address

        return api.create_order(
            origin_lat=float(shipment.origin_latitude),
            origin_lng=float(shipment.origin_longitude),
            origin_address=shipment.origin_address or '',
            origin_phone='',  # از انبار
            origin_name='XigmaHardware',
            dest_lat=float(dest.latitude) if dest else float(shipment.destination_latitude),
            dest_lng=float(dest.longitude) if dest else float(shipment.destination_longitude),
            dest_address=dest.full_address if dest else '',
            dest_phone=dest.recipient_mobile if dest else '',
            dest_name=dest.recipient_name if dest else '',
            package_description=shipment.package_description or '',
            package_weight=float(shipment.package_weight_kg) if shipment.package_weight_kg else None,
            vehicle_type=courier.vehicle_type,
        )