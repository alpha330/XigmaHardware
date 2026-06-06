import logging
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.payment.models import PaymentGateway, PaymentLog
from apps.payment.enums import GatewayType, PaymentStatus
from apps.payment.services.payping import PayPingGateway

logger = logging.getLogger(__name__)


class PaymentService:
    """
    سرویس اصلی پرداخت

    عملیات:
    - انتخاب درگاه مناسب
    - ایجاد پرداخت
    - ریدایرکت به درگاه
    - تایید پرداخت
    - برگشت وجه
    """

    GATEWAY_CLASSES = {
        'payping': PayPingGateway,
        # 'zarinpal': ZarinPalGateway,
        # 'crypto': CryptoGateway,
    }

    @classmethod
    def get_default_gateway(cls):
        """دریافت درگاه پیش‌فرض فعال"""
        gateway = PaymentGateway.objects.filter(
            is_active=True,
            is_default=True,
        ).first()

        if not gateway:
            gateway = PaymentGateway.objects.filter(
                is_active=True,
                gateway_type=GatewayType.PAYPING,
            ).first()

        if not gateway:
            raise ValueError(_('No active payment gateway found.'))

        return gateway

    @classmethod
    def get_gateway_instance(cls, gateway_config):
        """دریافت نمونه درگاه بر اساس نوع"""
        gateway_class = cls.GATEWAY_CLASSES.get(gateway_config.gateway_type)

        if not gateway_class:
            raise ValueError(f'Gateway type {gateway_config.gateway_type} not supported.')

        return gateway_class(gateway_config)

    @classmethod
    @db_transaction.atomic
    def create_payment(cls, user, amount, description='', invoice=None,
                       gateway_config=None, callback_url=None, request=None):
        """
        ایجاد پرداخت جدید

        Args:
            user: کاربر
            amount: مبلغ
            description: توضیحات
            invoice: فاکتور مرتبط
            gateway_config: درگاه (پیش‌فرض = default)
            callback_url: آدرس بازگشت
            request: request برای IP

        Returns:
            dict: نتیجه با payment_log و payment_url
        """
        # انتخاب درگاه
        if not gateway_config:
            gateway_config = cls.get_default_gateway()

        # اعتبارسنجی مبلغ
        if amount < gateway_config.min_amount:
            raise ValueError(
                _(f'Minimum amount is {gateway_config.min_amount:,} Rials.')
            )

        if amount > gateway_config.max_amount:
            raise ValueError(
                _(f'Maximum amount is {gateway_config.max_amount:,} Rials.')
            )

        # ایجاد لاگ پرداخت
        payment_log = PaymentLog.objects.create(
            user=user,
            gateway=gateway_config,
            invoice=invoice,
            amount=amount,
            status=PaymentStatus.PENDING,
            description=description[:500] if description else '',
            payer_ip=cls._get_client_ip(request) if request else None,
        )

        # دریافت نمونه درگاه
        gateway = cls.get_gateway_instance(gateway_config)

        # آماده‌سازی callback URL
        if not callback_url:
            from django.conf import settings
            callback_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            callback_url = f"{callback_url}/api/v1/payment/callback/{payment_log.id}/"

        if gateway_config.callback_url:
            callback_url = gateway_config.callback_url

        # ایجاد پرداخت در درگاه
        result = gateway.create_payment(
            amount=amount,
            description=description,
            payer_name=user.get_display_name() if user else '',
            payer_email=user.email if user else '',
            payer_mobile=user.mobile if user else '',
            callback_url=callback_url,
        )

        # ذخیره پاسخ درگاه
        payment_log.gateway_request = {
            'amount': int(amount),
            'description': description,
            'callback_url': callback_url,
        }
        payment_log.gateway_response = result

        if result.get('success'):
            payment_log.mark_redirected(result.get('gateway_code'))

            logger.info(
                f"Payment created: {payment_log.id} -> {gateway_config.name}"
            )

            return {
                'success': True,
                'payment_log': payment_log,
                'payment_url': result.get('payment_url'),
                'gateway_code': result.get('gateway_code'),
            }
        else:
            payment_log.mark_failed(result.get('error', 'Gateway error'))

            logger.error(f"Payment creation failed: {result.get('error')}")

            return {
                'success': False,
                'error': result.get('error', 'Payment creation failed'),
                'payment_log': payment_log,
            }

    @classmethod
    @db_transaction.atomic
    def verify_payment(cls, payment_log_id, callback_data=None):
        """
        تایید پرداخت (Callback)

        Args:
            payment_log_id: شناسه لاگ پرداخت
            callback_data: داده‌های callback از درگاه

        Returns:
            dict
        """
        try:
            payment_log = PaymentLog.objects.select_related(
                'gateway', 'user', 'invoice'
            ).get(id=payment_log_id)
        except PaymentLog.DoesNotExist:
            return {'success': False, 'error': 'Payment log not found.'}

        if payment_log.is_verified:
            return {
                'success': True,
                'already_verified': True,
                'payment_log': payment_log,
            }

        # ذخیره callback data
        if callback_data:
            payment_log.callback_data = callback_data
            payment_log.save()

        # دریافت نمونه درگاه
        gateway = cls.get_gateway_instance(payment_log.gateway)

        # تایید پرداخت
        result = gateway.verify_payment(
            gateway_code=payment_log.gateway_code,
            amount=payment_log.amount,
        )

        if result.get('success'):
            payment_log.mark_verified(result.get('reference_code'))

            # اگر فاکتور داره، پرداخت رو ثبت کن
            if payment_log.invoice:
                from apps.financial.services.invoice_service import InvoiceService

                InvoiceService.record_payment(
                    invoice=payment_log.invoice,
                    amount=payment_log.amount,
                    payment_method='online_gateway',
                    reference_code=result.get('reference_code', ''),
                    verified_by=None,
                )

            logger.info(f"Payment verified: {payment_log.id}")

            return {
                'success': True,
                'payment_log': payment_log,
                'reference_code': result.get('reference_code'),
            }
        else:
            payment_log.mark_failed(result.get('error', 'Verification failed'))

            return {
                'success': False,
                'error': result.get('error', 'Verification failed'),
                'payment_log': payment_log,
            }

    @staticmethod
    def _get_client_ip(request):
        """دریافت IP کاربر"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')