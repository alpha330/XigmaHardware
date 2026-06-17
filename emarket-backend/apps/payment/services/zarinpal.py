import requests
from django.utils.translation import gettext_lazy as _
from .base import BaseGateway

class ZarinPalGateway(BaseGateway):
    name = "ZarinPal"
    gateway_type = "zarinpal"
    supports_sandbox = True
    supports_refund = True

    # آدرس‌های زرین‌پال (Sandbox و Production)
    SANDBOX_URL = "https://sandbox.zarinpal.com/pg/v4/payment/"
    PRODUCTION_URL = "https://api.zarinpal.com/pg/v4/payment/"

    def __init__(self, config):
        super().__init__(config)
        self.base_url = self.SANDBOX_URL if self.is_test else self.PRODUCTION_URL

    # -------------------- ایجاد پرداخت --------------------
    def create_payment(self, amount, description, payer_name, payer_email, payer_mobile, callback_url):
        url = f"{self.base_url}request.json"

        payload = {
            "merchant_id": self.api_key,
            "amount": int(amount),
            "description": description,
            "callback_url": callback_url,
            "metadata": {
                # 🎯 اصلاح: تبدیل اجباری به رشته
                "mobile": str(payer_mobile) if payer_mobile else '',
                "email": str(payer_email) if payer_email else ''
            }
        }
        print(payload)
        try:
            resp = requests.post(url, json=payload, timeout=30)
            data = resp.json()

            if data.get('data', {}).get('code') == 100:
                authority = data['data']['authority']
                # آدرس پرداخت زرین‌پال
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

    # -------------------- تأیید پرداخت --------------------
    def verify_payment(self, gateway_code, amount, **kwargs):
        url = f"{self.base_url}verify.json"
        payload = {
            "merchant_id": self.api_key,
            "amount": int(amount),
            "authority": gateway_code
        }

        # 🎯 این لاگ رو اضافه کن تا مطمئن بشیم زرین‌پال داره تاییدیه رو برمی‌گردونه
        print(f"DEBUG: Verifying ZarinPal - Authority: {gateway_code}, Amount: {amount}")

        try:
            resp = requests.post(url, json=payload, timeout=30)
            data = resp.json()

            print(f"DEBUG: ZarinPal Response: {data}")

            if data.get('data', {}).get('code') == 100:
                return {
                    'success': True,
                    'reference_code': str(data['data']['ref_id']),
                    'data': data,
                }
            else:
                return {'success': False, 'error': f"Verification failed: {data.get('errors')}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # -------------------- متدهای اجباری پایه --------------------
    def get_payment_info(self, gateway_code):
        # زرین‌پال متد استعلام تکی به این شکل ندارد، معمولاً از طریق verify چک می‌شود
        return {'success': False, 'error': 'Not supported'}