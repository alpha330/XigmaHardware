import requests
from django.utils.translation import gettext_lazy as _
from .base import BaseGateway

class ZarinPalGateway(BaseGateway):
    name = "ZarinPal"
    gateway_type = "zarinpal"
    supports_sandbox = True
    supports_refund = True

    SANDBOX_URL = "https://sandbox.zarinpal.com/pg/v4/payment/"
    PRODUCTION_URL = "https://api.zarinpal.com/pg/v4/payment/"

    def __init__(self, config):
        super().__init__(config)
        self.base_url = self.SANDBOX_URL if self.is_test else self.PRODUCTION_URL

    def create_payment(self, amount, description, payer_name, payer_email, payer_mobile, callback_url):
        url = f"{self.base_url}request.json"

        payload = {
            "merchant_id": self.api_key,
            "amount": int(amount),
            "description": description,
            "callback_url": callback_url,
            "metadata": {
                "mobile": str(payer_mobile) if payer_mobile else '',
                "email": str(payer_email) if payer_email else ''
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=30, verify=False)
            data = resp.json()

            if data.get('data', {}).get('code') == 100:
                authority = data['data']['authority']
                payment_url = f"https://{'sandbox' if self.is_test else 'www'}.zarinpal.com/pg/StartPay/{authority}"
                return {
                    'success': True,
                    'gateway_code': authority,
                    'payment_url': payment_url,
                    'data': data,
                }
            else:
                return {'success': False, 'error': f"Error code: {data.get('errors')}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verify_payment(self, gateway_code, amount, **kwargs):
        url = f"{self.base_url}verify.json"
        payload = {
            "merchant_id": self.api_key,
            "amount": int(amount),
            "authority": gateway_code
        }

        print(f"[ZarinPal] Verifying - Authority: {gateway_code}, Amount: {amount}")

        try:
            resp = requests.post(url, json=payload, timeout=30, verify=False)
            data = resp.json()
            print(f"[ZarinPal] Verify Response: {data}")

            code = data.get('data', {}).get('code')

            if code == 100:
                return {
                    'success': True,
                    'reference_code': str(data['data']['ref_id']),
                    'data': data,
                }
            elif code == 101:
                # Already verified - treat as success
                return {
                    'success': True,
                    'already_verified': True,
                    'reference_code': str(data['data'].get('ref_id', gateway_code)),
                    'data': data,
                }
            else:
                return {
                    'success': False,
                    'error': f"Verification failed with code: {code}",
                    'data': data.get('errors')
                }
        except Exception as e:
            print(f"[ZarinPal] Verify Exception: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_payment_info(self, gateway_code):
        return {'success': False, 'error': 'Not supported'}
