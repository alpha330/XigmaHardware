"""
یکپارچگی با Alopeyk (الوپیک)

مستندات API: https://alopeyk.com/api/docs
GitHub: https://github.com/AloPeyk

ویژگی‌ها:
- استعلام قیمت لحظه‌ای
- ثبت سفارش
- لغو سفارش
- پیگیری وضعیت
- پیک موتوری و خودرو
- مسیریابی هوشمند
"""

import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from .base import BaseCourierAPI

logger = logging.getLogger(__name__)


class AlopeykAPI(BaseCourierAPI):
    """
    کلاینت API الوپیک

    API Base URL:
    - Production: https://api.alopeyk.com/api/v2/
    - Sandbox: https://sandbox.alopeyk.com/api/v2/

    احراز هویت:
    - API Key در هدر Authorization
    - یا JWT Token
    """

    name = "Alopeyk"
    supports_sandbox = True

    BASE_URL = "https://api.alopeyk.com/api/v2/"
    SANDBOX_URL = "https://sandbox.alopeyk.com/api/v2/"

    # نوع وسایل نقلیه در Alopeyk
    VEHICLE_TYPES = {
        'motorcycle': 'MOTORCYCLE',
        'car': 'CAR',
        'pickup': 'PICKUP',
        'van': 'VAN',
        'truck': 'TRUCK',
    }

    def __init__(self, api_key: str = "", api_secret: str = "", is_sandbox: bool = False):
        super().__init__(api_key, api_secret, is_sandbox)
        # Alopeyk از API Key در هدر استفاده می‌کنه
        self.api_key = api_key
        self.token = None  # Alopeyk ممکنه JWT هم بده

    def authenticate(self) -> bool:
        """
        احراز هویت Alopeyk

        Alopeyk دو روش داره:
        1. API Key مستقیم در هدر
        2. JWT Token با refresh

        POST /auth/login
        """
        if self.api_key:
            # تست اعتبار API Key
            try:
                response = requests.get(
                    f"{self.base_url}profile",
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    timeout=10
                )
                return response.status_code == 200
            except:
                return False

        # اگر api_secret داریم، لاگین کنیم
        if self.api_secret:
            try:
                url = f"{self.base_url}auth/login"
                payload = {
                    'api_key': self.api_key,
                    'api_secret': self.api_secret,
                }

                response = requests.post(url, json=payload, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get('token')
                    return True
            except Exception as e:
                logger.error(f"Alopeyk auth error: {str(e)}")

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
        استعلام قیمت الوپیک

        POST /orders/price/estimate
        """
        url = f"{self.base_url}orders/price/estimate"

        payload = {
            'transport_type': self.VEHICLE_TYPES.get(vehicle_type, 'MOTORCYCLE'),
            'origin_lat': origin_lat,
            'origin_lng': origin_lng,
            'dest_lat': dest_lat,
            'dest_lng': dest_lng,
        }

        if package_weight:
            payload['weight'] = package_weight

        self.log_request('POST', url, payload)

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=15
            )

            self.log_response(response.status_code, response.text)

            if response.status_code == 200:
                data = response.json()

                return {
                    'success': True,
                    'price': data.get('price', 0),  # ریال
                    'distance_km': data.get('distance', 0) / 1000,
                    'duration_min': data.get('duration', 0),
                    'currency': 'IRR',
                    'data': {
                        'base_price': data.get('base_price', 0),
                        'distance_fee': data.get('distance_fee', 0),
                        'traffic_fee': data.get('traffic_fee', 0),
                        'total_price': data.get('price', 0),
                        'transport_type': vehicle_type,
                    },
                }

            return {
                'success': False,
                'error': f"Alopeyk error: {response.text[:200]}",
                'data': response.json() if response.text else {},
            }

        except requests.Timeout:
            return {'success': False, 'error': 'Alopeyk timeout. Please try again.'}
        except Exception as e:
            logger.error(f"Alopeyk estimate error: {str(e)}")
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
        ثبت سفارش در الوپیک

        POST /orders
        """
        url = f"{self.base_url}orders"

        payload = {
            'transport_type': self.VEHICLE_TYPES.get(vehicle_type, 'MOTORCYCLE'),
            'origin': {
                'lat': origin_lat,
                'lng': origin_lng,
                'address': origin_address[:500],
                'person_name': origin_name,
                'person_phone': origin_phone,
            },
            'destination': {
                'lat': dest_lat,
                'lng': dest_lng,
                'address': dest_address[:500],
                'person_name': dest_name,
                'person_phone': dest_phone,
            },
            'description': package_description[:200] if package_description else '',
            'has_return': False,
            'cashed': False,  # پرداخت توسط فرستنده
        }

        if package_weight:
            payload['weight'] = package_weight

        if callback_url:
            payload['webhook_url'] = callback_url

        self.log_request('POST', url, payload)

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=20
            )

            self.log_response(response.status_code, response.text)

            if response.status_code in [200, 201]:
                data = response.json()
                order = data.get('order', data)

                return {
                    'success': True,
                    'order_id': str(order.get('id', '')),
                    'tracking_code': order.get('tracking_code', ''),
                    'status': order.get('status', 'pending'),
                    'price': order.get('price', 0),
                    'estimated_pickup_time': order.get('estimated_pickup_time'),
                    'estimated_delivery_time': order.get('estimated_delivery_time'),
                    'courier_name': order.get('courier', {}).get('name', ''),
                    'courier_phone': order.get('courier', {}).get('phone', ''),
                    'data': order,
                }

            return {
                'success': False,
                'error': f"Alopeyk order creation failed: {response.text[:200]}",
                'data': response.json() if response.text else {},
            }

        except requests.Timeout:
            return {'success': False, 'error': 'Alopeyk timeout.'}
        except Exception as e:
            logger.error(f"Alopeyk create order error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def cancel_order(self, order_id: str, reason: str = "") -> Dict[str, Any]:
        """
        لغو سفارش الوپیک

        POST /orders/{id}/cancel
        """
        url = f"{self.base_url}orders/{order_id}/cancel"

        payload = {'reason': reason} if reason else {}

        self.log_request('POST', url, payload)

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Order cancelled successfully.',
                    'data': response.json(),
                }

            return {
                'success': False,
                'error': f"Cancel failed: {response.text[:200]}",
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def track_order(self, order_id: str) -> Dict[str, Any]:
        """
        پیگیری سفارش الوپیک

        GET /orders/{id}
        """
        url = f"{self.base_url}orders/{order_id}"

        self.log_request('GET', url)

        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                order = data.get('order', data)
                courier = order.get('courier', {})

                return {
                    'success': True,
                    'status': order.get('status', 'unknown'),
                    'courier_name': courier.get('name', ''),
                    'courier_phone': courier.get('phone', ''),
                    'courier_lat': courier.get('current_lat'),
                    'courier_lng': courier.get('current_lng'),
                    'estimated_delivery': order.get('estimated_delivery_time'),
                    'tracking_events': order.get('tracking_events', []),
                    'data': order,
                }

            return {
                'success': False,
                'error': f"Tracking failed: {response.text[:200]}",
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}