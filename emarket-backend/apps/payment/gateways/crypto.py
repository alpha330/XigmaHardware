"""
درگاه پرداخت کریپتو (آینده)

ویژگی‌ها:
- پرداخت با Bitcoin, Ethereum, Tether (TRC20)
- تایید خودکار از طریق WebSocket/API
- تولید آدرس یکتا برای هر پرداخت
"""

from typing import Dict, Any
from .base import BaseGateway


class CryptoGateway(BaseGateway):
    """
    درگاه پرداخت ارز دیجیتال

    آماده برای پیاده‌سازی با:
    - BlockCypher API
    - Infura
    - TronGrid
    - یا صرافی‌های داخلی
    """

    name = "Cryptocurrency"
    gateway_type = "crypto"
    supports_sandbox = True
    supports_refund = True

    # شبکه‌های پشتیبانی شده
    SUPPORTED_NETWORKS = ['TRC20', 'ERC20', 'BEP20', 'BTC', 'ETH']

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
        ایجاد آدرس پرداخت کریپتو

        TODO: پیاده‌سازی کامل
        """
        network = self.extra_config.get('network', 'TRC20')
        wallet = self.config.wallet_address

        return {
            'success': False,
            'error': 'Cryptocurrency payment not yet implemented.',
            'message': 'Coming soon!',
            'payment_info': {
                'network': network,
                'wallet_address': wallet,
                'amount_crypto': '0.00',
                'amount_irr': amount,
            },
        }

    def verify_payment(
        self,
        gateway_code: str,
        amount: int,
    ) -> Dict[str, Any]:
        """تایید پرداخت کریپتو"""
        return {
            'success': False,
            'error': 'Not implemented',
        }

    def get_payment_info(
        self,
        gateway_code: str,
    ) -> Dict[str, Any]:
        """استعلام پرداخت کریپتو"""
        return {
            'success': False,
            'error': 'Not implemented',
        }