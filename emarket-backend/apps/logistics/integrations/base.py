"""
کلاس پایه برای API های پیک خارجی
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseCourierAPI(ABC):
    """
    Abstract Base Class برای API پیک‌های خارجی

    هر سرویس جدید (Alopeyk, SnappBox, ...) باید این متدها رو پیاده‌سازی کنه:

    متدهای اجباری:
    - authenticate: احراز هویت
    - get_price_estimate: استعلام قیمت
    - create_order: ثبت سفارش
    - cancel_order: لغو سفارش
    - track_order: پیگیری وضعیت

    متدهای اختیاری:
    - get_order_details: جزئیات سفارش
    - get_active_couriers: لیست پیک‌های فعال
    """

    # نام سرویس
    name: str = "Base Courier"

    # آیا sandbox داره؟
    supports_sandbox: bool = False

    # URL های API
    BASE_URL: str = ""
    SANDBOX_URL: str = ""

    def __init__(self, api_key: str = "", api_secret: str = "", is_sandbox: bool = False):
        """
        Args:
            api_key: کلید API
            api_secret: رمز API
            is_sandbox: حالت تست
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.is_sandbox = is_sandbox
        self.token = None

        self.base_url = self.SANDBOX_URL if is_sandbox and self.supports_sandbox else self.BASE_URL

        logger.info(f"Initialized {self.name} (sandbox={is_sandbox})")

    @abstractmethod
    def authenticate(self) -> bool:
        """
        احراز هویت و دریافت توکن

        Returns:
            bool: موفقیت‌آمیز بودن
        """
        pass

    @abstractmethod
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
        استعلام قیمت ارسال

        Args:
            origin_lat: عرض جغرافیایی مبدا
            origin_lng: طول جغرافیایی مبدا
            dest_lat: عرض جغرافیایی مقصد
            dest_lng: طول جغرافیایی مقصد
            vehicle_type: نوع وسیله نقلیه
            package_weight: وزن بسته (kg)

        Returns:
            {
                'success': bool,
                'price': float,           # قیمت به ریال
                'distance_km': float,     # مسافت
                'duration_min': int,      # زمان تخمینی
                'currency': str,
                'data': dict,             # اطلاعات اضافی
                'error': str,
            }
        """
        pass

    @abstractmethod
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
        ثبت سفارش ارسال

        Returns:
            {
                'success': bool,
                'order_id': str,          # کد سفارش در سرویس
                'tracking_code': str,     # کد رهگیری
                'status': str,
                'price': float,
                'estimated_pickup_time': str,
                'estimated_delivery_time': str,
                'courier_name': str,
                'courier_phone': str,
                'data': dict,
                'error': str,
            }
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, reason: str = "") -> Dict[str, Any]:
        """
        لغو سفارش

        Returns:
            {'success': bool, 'message': str, 'error': str}
        """
        pass

    @abstractmethod
    def track_order(self, order_id: str) -> Dict[str, Any]:
        """
        پیگیری وضعیت سفارش

        Returns:
            {
                'success': bool,
                'status': str,
                'courier_name': str,
                'courier_phone': str,
                'courier_lat': float,
                'courier_lng': float,
                'estimated_delivery': str,
                'tracking_events': list,
                'error': str,
            }
        """
        pass

    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """جزئیات سفارش (اختیاری)"""
        return {'success': False, 'error': 'Not implemented'}

    def get_headers(self) -> Dict[str, str]:
        """هدرهای استاندارد"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'XigmaHardware/1.0',
        }

        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        elif self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        return headers

    def log_request(self, method: str, url: str, payload: dict = None):
        """لاگ request"""
        logger.info(f"{self.name} {method} {url}")
        if payload:
            logger.debug(f"Payload: {payload}")

    def log_response(self, status_code: int, response_text: str):
        """لاگ response"""
        if status_code in [200, 201]:
            logger.info(f"{self.name} Response: {status_code}")
        else:
            logger.error(f"{self.name} Error {status_code}: {response_text[:300]}")

    def __str__(self):
        return f"{self.name} API ({'Test' if self.is_sandbox else 'Live'})"