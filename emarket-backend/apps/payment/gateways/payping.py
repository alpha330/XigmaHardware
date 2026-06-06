"""
پیاده‌سازی درگاه PayPing

مستندات رسمی: https://docs.payping.ir/
GitHub: https://github.com/payping/IR-REST-API-Client

ویژگی‌ها:
- پرداخت با ریدایرکت
- تایید پرداخت
- استعلام پرداخت
- Sandbox mode با توکن تست
"""

import logging
import requests
from typing import Dict, Any
from django.utils.translation import gettext_lazy as _
from .base import BaseGateway

logger = logging.getLogger(__name__)


class PayPingGateway(BaseGateway):
    """
    درگاه پرداخت PayPing

    توکن تست (Sandbox):
    - می‌تونی از پنل PayPing توکن تست بگیری
    - یا از توکن عمومی استفاده کنی

    API Endpoints:
    - Sandbox: https://api.payping.ir/v2/
    - Production: https://api.payping.ir/v2/
    """

    name = "PayPing"
    gateway_type = "payping"
    supports_sandbox = True
    supports_refund = False  # PayPing از طریق API refund نداره

    # URL های API
    SANDBOX_BASE_URL = "https://api.payping.ir/v2/"
    PRODUCTION_BASE_URL = "https://api.payping.ir/v2/"

    # URL پرداخت
    SANDBOX_PAYMENT_URL = "https://api.payping.ir/v2/pay/goto/{code}"
    PRODUCTION_PAYMENT_URL = "https://api.payping.ir/v2/pay/goto/{code}"

    def __init__(self, config):
        super().__init__(config)

        # تنظیم URL ها بر اساس mode
        if self.is_test:
            self.base_url = self.SANDBOX_BASE_URL
            self.payment_base_url = self.SANDBOX_PAYMENT_URL
        else:
            self.base_url = self.PRODUCTION_BASE_URL
            self.payment_base_url = self.PRODUCTION_PAYMENT_URL

        logger.info(f"PayPing initialized: {self.base_url}")

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
        ایجاد پرداخت در PayPing

        PayPing API:
        POST /v2/pay
        Body: { amount, payerIdentity, payerName, description, returnUrl, clientRefId }
        """
        # اعتبارسنجی
        self.validate_amount(amount)

        url = f"{self.base_url}pay"

        payload = {
            'amount': int(amount),
            'payerIdentity': payer_mobile or payer_email or payer_name or '',
            'payerName': payer_name or '',
            'description': (description or 'Payment')[:200],
            'returnUrl': callback_url,
            'clientRefId': order_id or '',
        }

        # لاگ
        self.log_request(url, 'POST', {**payload, 'amount': amount})

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=30,
            )

            self.log_response(response.status_code, response.text)

            if response.status_code == 200:
                data = response.json()
                code = data.get('code')

                return {
                    'success': True,
                    'gateway_code': code,
                    'payment_url': self.payment_base_url.format(code=code),
                    'message': 'Payment created successfully.',
                    'data': {
                        'code': code,
                        'payping_response': data,
                    },
                }

            # خطاهای PayPing
            error_messages = {
                400: 'Invalid request parameters.',
                401: 'Invalid API key.',
                403: 'Access denied.',
                422: 'Validation error.',
                500: 'PayPing server error.',
            }

            error_msg = error_messages.get(
                response.status_code,
                f'PayPing error: {response.text[:200]}'
            )

            return {
                'success': False,
                'error': error_msg,
                'data': response.json() if response.text else {},
            }

        except requests.Timeout:
            logger.error("PayPing timeout")
            return {
                'success': False,
                'error': 'Gateway timeout. Please try again.',
            }
        except requests.ConnectionError:
            logger.error("PayPing connection error")
            return {
                'success': False,
                'error': 'Cannot connect to payment gateway.',
            }
        except Exception as e:
            logger.error(f"PayPing unexpected error: {str(e)}")
            return {
                'success': False,
                'error': 'An unexpected error occurred.',
            }

    def verify_payment(
        self,
        gateway_code: str,
        amount: int,
    ) -> Dict[str, Any]:
        """
        تایید پرداخت در PayPing

        PayPing API:
        POST /v2/pay/verify
        Body: { amount, refId }
        """
        url = f"{self.base_url}pay/verify"

        payload = {
            'amount': int(amount),
            'refId': gateway_code,
        }

        self.log_request(url, 'POST', {'refId': gateway_code, 'amount': amount})

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.get_headers(),
                timeout=30,
            )

            self.log_response(response.status_code, response.text)

            if response.status_code == 200:
                data = response.json()

                return {
                    'success': True,
                    'reference_code': data.get('refcode') or data.get('refCode') or gateway_code,
                    'card_number': data.get('cardNumber', ''),
                    'message': 'Payment verified successfully.',
                    'data': {
                        'refcode': data.get('refcode'),
                        'card_number': data.get('cardNumber'),
                        'payping_response': data,
                    },
                }

            # خطاهای تایید
            if response.status_code == 400:
                # مبلغ اشتباه یا قبلاً تایید شده
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Verification failed.')
                except:
                    error_msg = 'Verification failed.'

                return {
                    'success': False,
                    'error': error_msg,
                    'data': response.json() if response.text else {},
                }

            return {
                'success': False,
                'error': f'Verification failed: {response.text[:200]}',
                'data': response.json() if response.text else {},
            }

        except requests.Timeout:
            # در صورت timeout، شاید پرداخت موفق بوده
            logger.warning("PayPing verify timeout - payment may be successful")
            return {
                'success': False,
                'error': 'Verification timeout. Please check payment status manually.',
                'needs_manual_check': True,
            }
        except Exception as e:
            logger.error(f"PayPing verify error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
            }

    def get_payment_info(
        self,
        gateway_code: str,
    ) -> Dict[str, Any]:
        """
        استعلام پرداخت از PayPing

        PayPing API:
        GET /v2/pay/{code}
        """
        url = f"{self.base_url}pay/{gateway_code}"

        self.log_request(url, 'GET')

        try:
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=30,
            )

            self.log_response(response.status_code, response.text)

            if response.status_code == 200:
                data = response.json()

                return {
                    'success': True,
                    'data': {
                        'code': data.get('code'),
                        'amount': data.get('amount'),
                        'status': data.get('status'),
                        'paid_at': data.get('paidAt'),
                        'card_number': data.get('cardNumber'),
                        'refcode': data.get('refcode'),
                        'description': data.get('description'),
                    },
                }

            return {
                'success': False,
                'error': f'Payment not found: {response.text[:200]}',
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def refund_payment(
        self,
        gateway_code: str,
        amount: int = None,
        reason: str = '',
    ) -> Dict[str, Any]:
        """
        برگشت وجه PayPing

        توجه: PayPing از طریق API امکان refund نداره
        باید از پنل PayPing انجام بشه
        """
        return {
            'success': False,
            'error': 'PayPing refund must be done manually from dashboard.',
            'message': 'Please login to PayPing dashboard to process refund.',
            'payping_url': 'https://app.payping.ir/',
        }