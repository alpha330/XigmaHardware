import requests
from django.utils.translation import gettext_lazy as _
from .base import BaseGateway

class PayPingGateway(BaseGateway):
    name = "PayPing"
    gateway_type = "payping"
    supports_sandbox = True
    supports_refund = True

    SANDBOX_BASE_URL = "https://api.payping.ir/v3/"
    PRODUCTION_BASE_URL = "https://api.payping.ir/v3/"

    def __init__(self, config):
        super().__init__(config)
        self.base_url = self.SANDBOX_BASE_URL if self.is_test else self.PRODUCTION_BASE_URL

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    # -------------------- ایجاد پرداخت --------------------
    def create_payment(self, amount, description, payer_name, payer_email, payer_mobile, callback_url):
        url = f"{self.base_url}pay"
        payload = {
            "amount": int(amount),
            "returnUrl": callback_url,
            "payerIdentity": payer_mobile or payer_email or '',
            "payerName": payer_name or '',
            "description": description[:200] if description else '',
            "clientRefId": '',   # می‌توان شماره فاکتور را گذاشت
        }

        try:
            resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'success': True,
                    'gateway_code': data['paymentCode'],
                    'payment_url': data['url'],          # لینک پرداخت مستقیم
                    'data': data,
                }
            else:
                return self._handle_error(resp)
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    # -------------------- تأیید پرداخت --------------------
    def verify_payment(self, gateway_code, amount, payment_ref_id=None, **kwargs):

        if not payment_ref_id:
            return {'success': False, 'error': 'payment_ref_id is required.'}

        url = f"{self.base_url}pay/verify"
        payload = {
            "paymentRefId": int(payment_ref_id),
            "paymentCode": gateway_code, # اینجا از gateway_code استفاده کنید
            "amount": int(amount),
        }
        try:
            resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'success': True,
                    'reference_code': str(data.get('paymentRefId', payment_ref_id)),
                    'card_number': data.get('cardNumber', ''),
                    'client_ref_id': data.get('clientRefId', ''),
                    'data': data,
                }
            elif resp.status_code == 409:
                data = resp.json()
                if data.get('metaData', {}).get('code') == 110:
                    return {
                        'success': True,
                        'already_verified': True,
                        'reference_code': str(payment_ref_id),
                        'card_number': '',
                        'data': data,
                    }
                return self._handle_error(resp)
            else:
                return self._handle_error(resp)
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    # -------------------- برگشت وجه --------------------
    def refund_payment(self, payment_ref_id, payment_code):
        url = f"{self.base_url}pay/reverse"
        payload = {
            "paymentRefId": int(payment_ref_id),
            "paymentCode": payment_code,
        }
        try:
            resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=30)
            if resp.status_code == 200:
                return {'success': True, 'data': resp.json()}
            return self._handle_error(resp)
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    # -------------------- دریافت اطلاعات پرداخت --------------------
    def get_payment_info(self, payment_code):
        url = f"{self.base_url}pay/{payment_code}"
        try:
            resp = requests.get(url, headers=self.get_headers(), timeout=30)
            if resp.status_code == 200:
                return {'success': True, 'data': resp.json()}
            return {'success': False, 'error': resp.text}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    # -------------------- ابزار کمکی --------------------
    def _handle_error(self, response):
        try:
            err = response.json()
            return {
                'success': False,
                'error': err.get('title', 'PayPing error'),
                'code': response.status_code,
                'details': err,
            }
        except:
            return {'success': False, 'error': response.text, 'code': response.status_code}