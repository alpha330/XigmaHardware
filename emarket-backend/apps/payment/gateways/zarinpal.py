"""
درگاه زرین‌پال (آینده)

مستندات: https://www.zarinpal.com/docs/
"""

from typing import Dict, Any
from .base import BaseGateway


class ZarinPalGateway(BaseGateway):
    """
    درگاه پرداخت زرین‌پال

    آماده برای پیاده‌سازی
    """

    name = "ZarinPal"
    gateway_type = "zarinpal"
    supports_sandbox = True
    supports_refund = True

    SANDBOX_URL = "https://sandbox.zarinpal.com/pg/v4/payment/"
    PRODUCTION_URL = "https://api.zarinpal.com/pg/v4/payment/"

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
        """ایجاد پرداخت زرین‌پال"""
        return {
            'success': False,
            'error': 'ZarinPal gateway not yet implemented.',
            'message': 'Coming soon!',
        }

    def verify_payment(
        self,
        gateway_code: str,
        amount: int,
    ) -> Dict[str, Any]:
        """تایید پرداخت زرین‌پال"""
        return {
            'success': False,
            'error': 'Not implemented',
        }

    def get_payment_info(
        self,
        gateway_code: str,
    ) -> Dict[str, Any]:
        """استعلام پرداخت"""
        return {
            'success': False,
            'error': 'Not implemented',
        }