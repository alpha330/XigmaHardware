import logging
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.payment.models import PaymentGateway, PaymentLog
from apps.payment.enums import GatewayType, PaymentStatus
from apps.payment.services.payping import PayPingGateway

logger = logging.getLogger(__name__)


class PaymentService:
    GATEWAY_CLASSES = {
        'payping': PayPingGateway,
    }

    @classmethod
    def get_default_gateway(cls):
        gateway = PaymentGateway.objects.filter(
            is_active=True, is_default=True
        ).first()
        if not gateway:
            gateway = PaymentGateway.objects.filter(
                is_active=True, gateway_type=GatewayType.PAYPING
            ).first()
        if not gateway:
            raise ValueError(_('No active payment gateway found.'))
        return gateway

    @classmethod
    def get_gateway_instance(cls, gateway_config):
        gateway_class = cls.GATEWAY_CLASSES.get(gateway_config.gateway_type)
        if not gateway_class:
            raise ValueError(
                f'Gateway type {gateway_config.gateway_type} not supported.'
            )
        return gateway_class(gateway_config)

    @classmethod
    @db_transaction.atomic
    def create_payment(cls, user, amount, description='', invoice=None,
                       gateway_config=None, callback_url=None, request=None):
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

        payment_log = PaymentLog.objects.create(
            user=user,
            gateway=gateway_config,
            invoice=invoice,
            amount=amount,
            status=PaymentStatus.PENDING,
            description=description[:500] if description else '',
            payer_ip=cls._get_client_ip(request) if request else None,
        )

        gateway = cls.get_gateway_instance(gateway_config)

        # 🔹 ارسال شناسه لاگ به درگاه (برای clientRefId)
        if hasattr(gateway, 'payment_log_id'):
            gateway.payment_log_id = str(payment_log.id)

        # 🔹 ارسال کد ملی کاربر (در صورت وجود)
        national_code = ''
        if user and hasattr(user, 'profile') and user.profile:
            national_code = user.profile.national_code or ''
        if hasattr(gateway, 'national_code'):
            gateway.national_code = national_code

        # آماده‌سازی callback URL
        if not callback_url:
            from django.conf import settings
            callback_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            callback_url = f"{callback_url}/api/v1/payment/callback/{payment_log.id}/"

        if gateway_config.callback_url:
            callback_url = gateway_config.callback_url

        # ایجاد پرداخت
        result = gateway.create_payment(
            amount=amount,
            description=description,
            payer_name=user.get_display_name() if user else '',
            payer_email=user.email if user else '',
            payer_mobile=user.mobile if user else '',
            callback_url=callback_url,
        )

        payment_log.gateway_request = {
            'amount': int(amount),
            'description': description,
            'callback_url': callback_url,
        }
        payment_log.gateway_response = result

        if result.get('success'):
            payment_log.mark_redirected(result.get('gateway_code'))
            logger.info(f"Payment created: {payment_log.id} -> {gateway_config.name}")
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

        if callback_data:
            payment_log.callback_data = callback_data
            payment_log.save()

        gateway = cls.get_gateway_instance(payment_log.gateway)

        # پارامترهای اضافی برای PayPing v3
        extra_kwargs = {}
        if payment_log.gateway.gateway_type == GatewayType.PAYPING:
            payment_ref_id = callback_data.get('paymentRefId') if callback_data else None
            if not payment_ref_id:
                # ممکن است در data تودرتو باشد (callback POST)
                payment_ref_id = callback_data.get('data', {}).get('paymentRefId')
            extra_kwargs['payment_ref_id'] = payment_ref_id

        result = gateway.verify_payment(
            gateway_code=payment_log.gateway_code,
            amount=payment_log.amount,
            **extra_kwargs
        )

        if result.get('success'):
            payment_log.mark_verified(result.get('reference_code'))
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
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')