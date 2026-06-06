"""
پکیج درگاه‌های پرداخت

هر درگاه جدید باید:
1. از BaseGateway ارث‌بری کنه
2. متدهای create_payment, verify_payment, get_payment_info رو پیاده‌سازی کنه
3. توی GATEWAY_CLASSES ثبت بشه
"""

from .base import BaseGateway
from .payping import PayPingGateway
# from .zarinpal import ZarinPalGateway      # آینده
# from .crypto import CryptoGateway           # آینده
# from .card_to_card import CardToCardGateway # آینده

__all__ = [
    'BaseGateway',
    'PayPingGateway',
]