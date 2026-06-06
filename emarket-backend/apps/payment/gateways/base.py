"""
کلاس پایه همه درگاه‌های پرداخت
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseGateway(ABC):
    """
    Abstract Base Class برای همه درگاه‌های پرداخت

    هر درگاه جدید باید این متدها رو پیاده‌سازی کنه:
    - create_payment: ایجاد تراکنش پرداخت
    - verify_payment: تایید پرداخت
    - get_payment_info: دریافت اطلاعات پرداخت
    - refund_payment: (اختیاری) برگشت وجه
    """

    # نام درگاه (برای نمایش)
    name: str = "Base Gateway"

    # نوع درگاه
    gateway_type: str = "base"

    # آیا از sandbox پشتیبانی می‌کنه؟
    supports_sandbox: bool = True

    # آیا از refund پشتیبانی می‌کنه؟
    supports_refund: bool = False

    # آیا از پرداخت خودکار (بدون ریدایرکت) پشتیبانی می‌کنه؟
    supports_direct_payment: bool = False

    def __init__(self, config):
        """
        Args:
            config: PaymentGateway instance
        """
        self.config = config
        self.is_test = config.mode == 'test'
        self.api_key = self._get_api_key()
        self.extra_config = config.extra_config or {}

        logger.info(f"Initialized {self.name} gateway (test={self.is_test})")

    def _get_api_key(self) -> str:
        """دریافت API Key مناسب بر اساس mode"""
        if self.is_test and self.config.sandbox_api_key:
            return self.config.sandbox_api_key
        return self.config.api_key or ''

    @abstractmethod
    def create_payment(
        self,
        amount: int,
        description: str = '',
        payer_name: str = '',
        payer_email: str = '',
        payer_mobile: str = '',
        callback_url: str = '',
        order_id: str = '',
    ) -> Dict[str, Any]:
        """
        ایجاد پرداخت جدید

        Args:
            amount: مبلغ به ریال
            description: توضیحات پرداخت
            payer_name: نام پرداخت‌کننده
            payer_email: ایمیل پرداخت‌کننده
            payer_mobile: موبایل پرداخت‌کننده
            callback_url: آدرس بازگشت بعد از پرداخت
            order_id: شماره سفارش/فاکتور (اختیاری)

        Returns:
            {
                'success': bool,
                'gateway_code': str,      # کد پیگیری درگاه
                'payment_url': str,       # URL برای ریدایرکت کاربر
                'message': str,           # پیام
                'data': dict,             # اطلاعات اضافی
                'error': str,             # متن خطا (در صورت失败)
            }
        """
        pass

    @abstractmethod
    def verify_payment(
        self,
        gateway_code: str,
        amount: int,
    ) -> Dict[str, Any]:
        """
        تایید پرداخت

        Args:
            gateway_code: کد پیگیری درگاه
            amount: مبلغ اصلی پرداخت

        Returns:
            {
                'success': bool,
                'reference_code': str,    # کد پیگیری بانک
                'card_number': str,       # شماره کارت پرداخت‌کننده (اختیاری)
                'message': str,
                'data': dict,
                'error': str,
            }
        """
        pass

    @abstractmethod
    def get_payment_info(
        self,
        gateway_code: str,
    ) -> Dict[str, Any]:
        """
        دریافت اطلاعات یک پرداخت

        Args:
            gateway_code: کد پیگیری درگاه

        Returns:
            {
                'success': bool,
                'data': dict,
                'error': str,
            }
        """
        pass

    def refund_payment(
        self,
        gateway_code: str,
        amount: Optional[int] = None,
        reason: str = '',
    ) -> Dict[str, Any]:
        """
        برگشت وجه (اختیاری)

        Args:
            gateway_code: کد پیگیری
            amount: مبلغ برگشتی (None = کل مبلغ)
            reason: دلیل برگشت

        Returns:
            {
                'success': bool,
                'reference_code': str,
                'message': str,
                'error': str,
            }
        """
        if not self.supports_refund:
            return {
                'success': False,
                'error': f'{self.name} does not support refund.',
            }

        raise NotImplementedError(f"Refund not implemented for {self.name}")

    def validate_amount(self, amount: int) -> bool:
        """
        اعتبارسنجی مبلغ

        Args:
            amount: مبلغ به ریال

        Returns:
            bool
        """
        min_amount = self.config.min_amount or 1000
        max_amount = self.config.max_amount or 500000000

        if amount < min_amount:
            raise ValueError(f'Amount must be at least {min_amount:,} Rials.')

        if amount > max_amount:
            raise ValueError(f'Amount cannot exceed {max_amount:,} Rials.')

        return True

    def get_headers(self) -> Dict[str, str]:
        """هدرهای استاندارد برای API calls"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'XigmaHardware/1.0',
        }

    def log_request(self, url: str, method: str, payload: dict = None):
        """لاگ request"""
        logger.info(f"{self.name} {method} {url}")
        if payload:
            # مخفی کردن اطلاعات حساس
            safe_payload = {k: ('***' if k in ['api_key', 'token', 'password'] else v)
                          for k, v in payload.items()}
            logger.debug(f"Payload: {safe_payload}")

    def log_response(self, status_code: int, response_text: str):
        """لاگ response"""
        logger.info(f"{self.name} Response: {status_code}")
        if status_code != 200:
            logger.error(f"{self.name} Error: {response_text[:500]}")

    def __str__(self):
        return f"{self.name} Gateway ({'Test' if self.is_test else 'Live'})"