import logging
from django.utils.translation import gettext_lazy as _
from zarinpal import ZarinPal
from zarinpal import PaymentRequest, PaymentVerification
from .base import BaseGateway

logger = logging.getLogger(__name__)

class ZarinPalGateway(BaseGateway):
    name = "ZarinPal"
    gateway_type = "zarinpal"
    supports_sandbox = True
    supports_refund = True       # زرین‌پال refund دارد

    # آدرس‌های sandbox و production (توسط SDK مدیریت می‌شود)
    def __init__(self, gateway_config):
        super().__init__(gateway_config)
        merchant_id = gateway_config.merchant_id or gateway_config.api_key
        if not merchant_id:
            raise ValueError("ZarinPal requires merchant_id or api_key.")

        sandbox = self.is_test
        # SDK جدید به‌صورت خودکار sandbox یا production را با boolean مشخص می‌کند
        self.zp = ZarinPal(merchant_id, sandbox=sandbox)

    def get_headers(self):
        return {}  # SDK از هدر اختصاصی استفاده نمی‌کند

    # ----- ایجاد پرداخت -----
    def create_payment(self, amount, description, payer_name, payer_email, payer_mobile, callback_url):
        # زرین‌پال مبلغ را به ریال می‌خواهد
        request = PaymentRequest(
            amount=int(amount),
            description=description[:200] if description else '',
            callback_url=callback_url,
            mobile=payer_mobile or '',
            email=payer_email or '',
        )
        try:
            response = self.zp.request(request)
            if response.status == 100:  # موفق
                return {
                    'success': True,
                    'gateway_code': response.authority,
                    'payment_url': response.url,
                    'data': {'authority': response.authority, 'url': response.url},
                }
            else:
                return {
                    'success': False,
                    'error': f"ZarinPal error: {response.status}",
                    'data': {'status': response.status},
                }
        except Exception as e:
            logger.error(f"ZarinPal request failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    # ----- تأیید پرداخت -----
    def verify_payment(self, gateway_code, amount, **kwargs):
        authority = gateway_code
        verification = PaymentVerification(
            amount=int(amount),
            authority=authority,
        )
        try:
            response = self.zp.verify(verification)
            if response.status == 100:   # وریفای موفق
                return {
                    'success': True,
                    'reference_code': str(response.ref_id),
                    'card_number': response.card_pan or '',
                    'data': {
                        'ref_id': response.ref_id,
                        'card_pan': response.card_pan,
                        'status': response.status,
                    },
                }
            elif response.status == 101:  # قبلاً وریفای شده
                return {
                    'success': True,
                    'already_verified': True,
                    'reference_code': str(response.ref_id) if response.ref_id else authority,
                    'card_number': response.card_pan or '',
                    'data': {'status': response.status},
                }
            else:
                return {
                    'success': False,
                    'error': f"Verification failed with status: {response.status}",
                    'data': {'status': response.status},
                }
        except Exception as e:
            logger.error(f"ZarinPal verify failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    # ----- دریافت اطلاعات پرداخت -----
    def get_payment_info(self, gateway_code):
        # زرین‌پال SDK متد inquiry دارد (بسته به نسخه ممکن است متفاوت باشد)
        try:
            # در برخی نسخه‌ها: self.zp.inquiry(authority=gateway_code)
            # اگر SDK شما متد inquiry ندارد، می‌توانید از REST API استفاده کنید
            # برای سادگی یک درخواست GET به آدرس زرین‌پال ارسال می‌کنیم
            import requests
            base = "https://sandbox.zarinpal.com/pg/v4/payment/" if self.is_test else "https://api.zarinpal.com/pg/v4/payment/"
            url = f"{base}{gateway_code}.json"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return {'success': True, 'data': resp.json()}
            return {'success': False, 'error': resp.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ----- برگشت وجه -----
    def refund_payment(self, gateway_code, amount=None):
        # زرین‌پال refund با authority و amount (اختیاری) انجام می‌شود
        # SDK ممکن است متد refund داشته باشد، در غیر این صورت از REST API استفاده کنید
        # این یک پیاده‌سازی ساده است
        import requests
        base = "https://sandbox.zarinpal.com/pg/v4/payment/" if self.is_test else "https://api.zarinpal.com/pg/v4/payment/"
        url = f"{base}refund"
        payload = {
            "authority": gateway_code,
            "merchant_id": self.config.merchant_id or self.api_key,
        }
        if amount:
            payload["amount"] = int(amount)
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                return {'success': True, 'data': resp.json()}
            return {'success': False, 'error': resp.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}