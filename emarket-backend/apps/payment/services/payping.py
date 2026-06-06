import logging
import requests
from django.utils.translation import gettext_lazy as _
from .base import BaseGateway

logger = logging.getLogger(__name__)


class PayPingGateway(BaseGateway):
    """
    پیاده‌سازی درگاه PayPing

    مستندات: https://docs.payping.ir/

    API های تست:
    - Sandbox: https://api.payping.ir/v2/
    - Token: sandbox توکن تست
    """

    SANDBOX_URL = 'https://api.payping.ir/v2/'
    PRODUCTION_URL = 'https://api.payping.ir/v2/'

    def __init__(self, gateway_config):
        super().__init__(gateway_config)
        self.base_url = self.SANDBOX_URL if self.is_test else self.PRODUCTION_URL

    def create_payment(self, amount, description, payer_name, payer_email, payer_mobile, callback_url):
        """
        ایجاد پرداخت PayPing

        Args:
            amount: مبلغ به ریال
            description: توضیحات
            payer_name: نام پرداخت‌کننده
            payer_email: ایمیل
            payer_mobile: موبایل
            callback_url: آدرس بازگشت

        Returns:
            dict
        """
        try:
            url = f"{self.base_url}pay"

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }

            payload = {
                'amount': int(amount),  # PayPing مبلغ رو به ریال می‌خواد
                'payerIdentity': payer_mobile or payer_email or '',
                'payerName': payer_name or '',
                'description': description[:200] if description else '',
                'returnUrl': callback_url,
                'clientRefId': '',  # می‌تونیم شماره فاکتور رو بفرستیم
            }

            logger.info(f"PayPing create payment: {payload}")

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            logger.info(f"PayPing response: {response.status_code} - {response.text}")

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'gateway_code': data.get('code'),
                    'payment_url': f"https://api.payping.ir/v2/pay/goto/{data.get('code')}",
                    'data': data,
                }
            else:
                return {
                    'success': False,
                    'error': f"PayPing error: {response.text}",
                    'data': response.json() if response.text else {},
                }

        except requests.RequestException as e:
            logger.error(f"PayPing request failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    def verify_payment(self, gateway_code, amount):
        """
        تایید پرداخت PayPing

        Args:
            gateway_code: کد پرداخت PayPing
            amount: مبلغ اصلی

        Returns:
            dict
        """
        try:
            url = f"{self.base_url}pay/verify"

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }

            payload = {
                'amount': int(amount),
                'refId': gateway_code,
            }

            logger.info(f"PayPing verify: {payload}")

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            logger.info(f"PayPing verify response: {response.status_code} - {response.text}")

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'reference_code': data.get('refcode') or data.get('refCode') or gateway_code,
                    'card_number': data.get('cardNumber', ''),
                    'data': data,
                }
            else:
                return {
                    'success': False,
                    'error': f"Verification failed: {response.text}",
                    'data': response.json() if response.text else {},
                }

        except requests.RequestException as e:
            logger.error(f"PayPing verify failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    def get_payment_info(self, gateway_code):
        """دریافت اطلاعات پرداخت"""
        try:
            url = f"{self.base_url}pay/{gateway_code}"

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                }

            return {'success': False, 'error': response.text}

        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}