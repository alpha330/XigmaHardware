"""
یکپارچگی با SnappBox (اسنپ باکس)

مستندات API: https://snapp-box.com/api/docs

ویژگی‌ها:
- استعلام قیمت
- ثبت سفارش
- لغو سفارش
- پیگیری وضعیت
"""

import logging
import requests
from typing import Dict, Any, Optional
from .base import BaseCourierAPI

logger = logging.getLogger(__name__)


class SnappBoxAPI(BaseCourierAPI):
    """
    کلاینت API اسنپ باکس

    API Base URL:
    - Production: https://api.snapp-box.com/v1/
    - Sandbox: https://sandbox.snapp-box.com/v1/
    """

    name = "SnappBox"
    supports_sandbox = True

    BASE_URL = "https://api.snapp-box.com/v1/"
    SANDBOX_URL = "https://sandbox.snapp-box.com/v1/"

    VEHICLE_TYPES = {
        'motorcycle': 'MOTOR',
        'car': 'CARGO',
        'pickup': 'PICKUP',
        'van': 'VAN',
    }

    def __init__(self, api_key: str = "", api_secret: str = "", is_sandbox: bool = False):
        super().__init__(api_key, api_secret, is_sandbox)

    def authenticate(self) -> bool:
        """
        احراز هویت SnappBox

        GET /auth/verify
        """
        try:
            response = requests.get(
                f"{self.base_url}auth/verify",
                headers={'X-API-Key': self.api_key},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def get_price_estimate(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        vehicle_type: str = "motorcycle",
        package_weight: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        استعلام قیمت SnappBox

        POST /orders/estimate
        """
        url = f"{self.base_url}orders/estimate"

        payload = {
            'origin': {'lat': origin_lat, 'lng': origin_lng},
            'destination': {'lat': dest_lat, 'lng': dest_lng},
            'vehicle_type': self.VEHICLE_TYPES.get(vehicle_type, 'MOTOR'),
        }

        self.log_request('POST', url, payload)

        try:
            response = requests.post(
                url,
                json=payload,
                headers={'X-API-Key': self.api_key, 'Content-Type': 'application/json'},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()

                return {
                    'success': True,
                    'price': data.get('total_price', 0),
                    'distance_km': data.get('distance', 0) / 1000,
                    'duration_min': data.get('eta', 0),
                    'currency': 'IRR',
                    'data': data,
                }

            return {'success': False, 'error': response.text[:200]}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_order(
        self,
        origin_lat: float,
        origin_lng: float,
        origin_address: str,
        origin_phone: str,
        origin_name: str,
        dest_lat: float,
        dest_lng: float,
        dest_address: str,
        dest_phone: str,
        dest_name: str,
        package_description: str = "",
        package_weight: Optional[float] = None,
        vehicle_type: str = "motorcycle",
        callback_url: str = "",
    ) -> Dict[str, Any]:
        """
        ثبت سفارش SnappBox

        POST /orders
        """
        url = f"{self.base_url}orders"

        payload = {
            'origin': {
                'lat': origin_lat, 'lng': origin_lng,
                'address': origin_address, 'name': origin_name, 'phone': origin_phone,
            },
            'destination': {
                'lat': dest_lat, 'lng': dest_lng,
                'address': dest_address, 'name': dest_name, 'phone': dest_phone,
            },
            'vehicle_type': self.VEHICLE_TYPES.get(vehicle_type, 'MOTOR'),
            'description': package_description,
            'webhook_url': callback_url,
        }

        if package_weight:
            payload['weight'] = package_weight

        self.log_request('POST', url, payload)

        try:
            response = requests.post(
                url,
                json=payload,
                headers={'X-API-Key': self.api_key, 'Content-Type': 'application/json'},
                timeout=20
            )

            if response.status_code in [200, 201]:
                data = response.json()

                return {
                    'success': True,
                    'order_id': str(data.get('id', '')),
                    'tracking_code': data.get('tracking_code', ''),
                    'status': data.get('status', 'pending'),
                    'price': data.get('price', 0),
                    'estimated_pickup_time': data.get('pickup_eta'),
                    'estimated_delivery_time': data.get('delivery_eta'),
                    'courier_name': '',
                    'courier_phone': '',
                    'data': data,
                }

            return {'success': False, 'error': response.text[:200]}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def cancel_order(self, order_id: str, reason: str = "") -> Dict[str, Any]:
        """لغو سفارش"""
        url = f"{self.base_url}orders/{order_id}/cancel"

        try:
            response = requests.post(
                url,
                headers={'X-API-Key': self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'message': 'Cancelled.'}

            return {'success': False, 'error': response.text[:200]}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def track_order(self, order_id: str) -> Dict[str, Any]:
        """پیگیری سفارش"""
        url = f"{self.base_url}orders/{order_id}"

        try:
            response = requests.get(
                url,
                headers={'X-API-Key': self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                return {
                    'success': True,
                    'status': data.get('status', 'unknown'),
                    'courier_name': data.get('courier', {}).get('name', ''),
                    'courier_phone': data.get('courier', {}).get('phone', ''),
                    'courier_lat': data.get('courier', {}).get('lat'),
                    'courier_lng': data.get('courier', {}).get('lng'),
                    'estimated_delivery': data.get('delivery_eta'),
                    'tracking_events': data.get('events', []),
                    'data': data,
                }

            return {'success': False, 'error': response.text[:200]}

        except Exception as e:
            return {'success': False, 'error': str(e)}