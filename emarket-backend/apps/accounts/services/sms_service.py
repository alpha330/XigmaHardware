import logging

from celery import shared_task
import ghasedak_sms
from django.conf import settings

logger = logging.getLogger(__name__)

class GhasedakSMSService:
    """
    سرویس مرکزی مدیریت پیامک با پنل قاصدک
    """
    OPT_OUT_MESSAGE = "\nلغو ۱۱"

    def __init__(self):
        self.api_key = getattr(settings, 'GHASEDAK_API_KEY', None)
        self.line_number = getattr(settings, 'GHASEDAK_LINE_NUMBER', None)
        self.otp_template = getattr(settings, 'GHASEDAK_OTP_TEMPLATE', None)
        self._client = None

    @property
    def client(self):
        if not self._client and self.api_key:
            self._client = ghasedak_sms.Ghasedak(self.api_key)
        return self._client

    def is_available(self):
        return bool(self.client)

    def _format_message(self, message):
        """اضافه کردن خودکار عبارت لغو به پایان پیام"""
        return f"{message}{self.OPT_OUT_MESSAGE}"

    def _handle_response(self, response, action_name, mobile):
        """مدیریت متمرکز پاسخ‌ها - فقط بر اساس استاتوس‌کد"""
        # قاصدک برای موفقیت، statusCode 200 را برمی‌گرداند
        # و معمولاً در دیکشنریِ پاسخ فیلدی به نام isSuccess: True دارد
        status_code = response.get('statusCode', 0)
        is_success = response.get('isSuccess', False)

        if is_success or status_code == 200:
            logger.info(f"{action_name} successful for {mobile}")
            return {'success': True, 'data': response}

        # فقط اگر کد 200 نبود، به عنوان خطا در نظر بگیر
        error_msg = response.get('message', 'Unknown Error')
        logger.error(f"{action_name} failed for {mobile}: {error_msg}")
        return {'success': False, 'error': error_msg}

    @shared_task(bind=True, max_retries=3)
    def send_otp_sms(self, mobile, code):
        from apps.accounts.services.sms_service import sms_service

        # استفاده از متدِ send_single چون پیام سفارشی است و لغو ۱۱ دارد
        result = sms_service.send_single(mobile, f"کد تایید شما در زیگما هاردور: {code}")

        if result.get('success'):
            return True # اگر موفق بود، تسک تمام شود
        else:
            # اگر خطا داشت، فقط در صورتی که خطا واقعی است retry کن
            error_msg = result.get('error', 'Unknown Error')
            raise self.retry(exc=Exception(error_msg), countdown=30)

    def send_otp_direct(self, mobile, code):
        """ارسال کد OTP به صورت پیامک تکی (با امضای خودکار لغو ۱۱)"""
        message = f"کد تایید شما در زیگما هاردور: {code}"
        return self.send_single(mobile, message)

    def send_single(self, mobile, message):
        """ارسال پیامک تکی با امضای خودکار 'لغو ۱۱'"""
        if not self.is_available():
            return {'success': False, 'error': 'SMS service unavailable'}

        try:
            sms_input = ghasedak_sms.SendSingleSmsInput(
                message=self._format_message(message),
                receptor=mobile,
                line_number=self.line_number
            )
            return self._handle_response(self.client.send_single_sms(sms_input), "Single SMS", mobile)
        except Exception as e:
            logger.error(f"Single SMS Exception: {str(e)}")
            return {'success': False, 'error': str(e)}

    def send_bulk(self, mobiles, message):
        """ارسال پیامک گروهی"""
        if not self.is_available():
            return {'success': False, 'error': 'SMS service unavailable'}

        try:
            bulk_input = ghasedak_sms.SendBulkInput(
                message=self._format_message(message),
                receptors=mobiles,
                line_number=self.line_number
            )
            return self._handle_response(self.client.send_bulk_sms(bulk_input), "Bulk SMS", len(mobiles))
        except Exception as e:
            logger.error(f"Bulk SMS Exception: {str(e)}")
            return {'success': False, 'error': str(e)}

    def get_balance(self):
        """دریافت مانده اعتبار پنل"""
        if not self.is_available():
            return None
        try:
            response = self.client.get_account_information()
            return response.get('data', {})
        except Exception as e:
            logger.error(f"Balance check failed: {str(e)}")
            return None

# نمونه سراسری سرویس
sms_service = GhasedakSMSService()