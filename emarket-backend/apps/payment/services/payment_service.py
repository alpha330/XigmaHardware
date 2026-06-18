import logging
from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.payment.models import PaymentGateway, PaymentLog
from apps.payment.enums import GatewayType, PaymentStatus
from apps.payment.services.payping import PayPingGateway
from apps.payment.services.zarinpal import ZarinPalGateway

logger = logging.getLogger(__name__)


class PaymentService:
    GATEWAY_CLASSES = {
        'payping': PayPingGateway,
        'zarinpal': ZarinPalGateway,
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

        if amount < gateway_config.min_amount or amount > gateway_config.max_amount:
            raise ValueError(_('Amount is out of allowed range.'))

        payment_log = PaymentLog.objects.create(
            user=user,
            gateway=gateway_config,
            invoice=invoice,
            amount=amount,
            status=PaymentStatus.PENDING,
            description=(description or '')[:500],
            payer_ip=cls._get_client_ip(request) if request else None,
        )

        try:
            gateway = cls.get_gateway_instance(gateway_config)
            gateway.payment_log_id = str(payment_log.id)

            if not callback_url:
                from django.conf import settings
                site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                callback_url = f"{site_url}/api/v1/payment/callback/{payment_log.id}/"

            result = gateway.create_payment(
                amount=amount,
                description=description,
                payer_name=user.get_display_name() if user else '',
                payer_email=user.email if user else '',
                payer_mobile=user.mobile if user else '',
                callback_url=callback_url,
            )

            if not result.get('success'):
                payment_log.mark_failed(result.get('error', 'Gateway error'))
                raise ValueError(result.get('error', 'Gateway request failed'))

            payment_log.mark_redirected(result.get('gateway_code'))
            payment_log.gateway_request = {'amount': int(amount), 'callback_url': callback_url}
            payment_log.save()

            return {
                'success': True,
                'payment_log': payment_log,
                'payment_url': result.get('payment_url'),
                'gateway_code': result.get('gateway_code'),
            }

        except Exception as e:
            logger.error(f"Payment Creation Error: {str(e)}")
            raise e

    @classmethod
    @db_transaction.atomic
    def verify_payment(cls, payment_log_id, callback_data=None):
        try:
            payment_log = PaymentLog.objects.select_related('gateway', 'user', 'invoice').get(id=payment_log_id)
        except PaymentLog.DoesNotExist:
            return {'success': False, 'error': 'Payment log not found.'}

        if payment_log.status == PaymentStatus.VERIFIED:
            return {'success': True, 'payment_log': payment_log, 'already_verified': True}

        gateway = cls.get_gateway_instance(payment_log.gateway)
        result = gateway.verify_payment(gateway_code=payment_log.gateway_code, amount=payment_log.amount)

        if result.get('success'):
            payment_log.mark_verified(result.get('reference_code'))

            # === منطق شارژ والت (بهبود یافته) ===
            charged_wallet = False
            amount_decimal = Decimal(str(payment_log.amount))  # همیشه Decimal

            if payment_log.invoice:
                from apps.financial.services.invoice_service import InvoiceService
                InvoiceService.record_payment(
                    invoice=payment_log.invoice,
                    amount=float(amount_decimal),  # اگر سرویس invoice float می‌خواد
                    payment_method='online_gateway',
                    reference_code=str(result.get('reference_code', '')),
                    verified_by=None,
                )

                inv_type = str(getattr(payment_log.invoice, 'invoice_type', '')).lower()
                if 'wallet' in inv_type or 'charge' in inv_type:
                    from apps.accounts.services.wallet_service import WalletService
                    if hasattr(payment_log.user, 'wallet'):
                        WalletService.deposit(
                            wallet=payment_log.user.wallet,
                            amount=amount_decimal,   # Decimal پاس بده
                            description="شارژ کیف پول از طریق درگاه",
                            reference_id=str(payment_log.id)
                        )
                        charged_wallet = True

            else:
                # اگر invoice وجود نداشت (شارژ مستقیم والت)
                desc = (payment_log.description or '').lower()
                if 'wallet' in desc or 'شارژ' in desc or 'charge' in desc:
                    from apps.accounts.services.wallet_service import WalletService
                    if hasattr(payment_log.user, 'wallet'):
                        WalletService.deposit(
                            wallet=payment_log.user.wallet,
                            amount=amount_decimal,
                            description="شارژ کیف پول از طریق درگاه (مستقیم)",
                            reference_id=str(payment_log.id)
                        )
                        charged_wallet = True

            logger.info(f"Payment verified successfully. Wallet charged: {charged_wallet}")
            return {
                'success': True,
                'payment_log': payment_log,
                'reference_code': result.get('reference_code'),
                'wallet_charged': charged_wallet
            }

        return {'success': False, 'error': 'Gateway verify failed'}

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', None)