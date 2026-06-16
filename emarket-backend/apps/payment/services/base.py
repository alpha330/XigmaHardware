from abc import ABC, abstractmethod
from django.utils.translation import gettext_lazy as _


class BaseGateway(ABC):
    """
    کلاس پایه برای همه درگاه‌های پرداخت

    هر درگاه جدید باید از این کلاس ارث‌بری کنه
    """

    def __init__(self, gateway_config):
        self.config = gateway_config
        self.api_key = gateway_config.effective_api_key
        self.is_test = gateway_config.mode == 'test'

    @abstractmethod
    def create_payment(self, amount, description, payer_name, payer_email, payer_mobile, callback_url):
        """
        ایجاد پرداخت در درگاه

        Returns:
            dict: {
                'success': bool,
                'gateway_code': str,  # کد پیگیری درگاه
                'payment_url': str,   # URL برای ریدایرکت
                'data': dict,         # اطلاعات اضافی
            }
        """
        pass

    @abstractmethod
    def verify_payment(self, gateway_code, amount, **kwargs):
        pass

    @abstractmethod
    def get_payment_info(self, gateway_code):
        """
        دریافت اطلاعات پرداخت

        Returns:
            dict
        """
        pass

    def get_name(self):
        return self.config.name

    def get_type(self):
        return self.config.gateway_type