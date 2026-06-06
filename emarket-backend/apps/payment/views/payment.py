import logging
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.conf import settings
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.payment.models import PaymentGateway, PaymentLog
from apps.payment.serializers.payment import (
    PaymentGatewaySerializer,
    PaymentLogSerializer,
    PaymentCreateSerializer,
    PaymentVerifySerializer,
    PaymentCallbackSerializer,
)
from apps.payment.permissions import CanManageGateway
from apps.payment.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


class PaymentViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet مدیریت پرداخت و درگاه‌ها

    Actions:
    - list: لیست درگاه‌های فعال
    - retrieve: جزئیات درگاه
    - pay: ایجاد پرداخت جدید
    - callback: بازگشت از درگاه
    - verify: تایید دستی پرداخت
    - payment_status: وضعیت پرداخت
    - my_payments: پرداخت‌های من
    """
    queryset = PaymentGateway.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PaymentGatewaySerializer
        elif self.action == 'pay':
            return PaymentCreateSerializer
        elif self.action == 'verify':
            return PaymentVerifySerializer
        elif self.action == 'callback':
            return PaymentCallbackSerializer
        return PaymentLogSerializer

    def get_permissions(self):
        if self.action == 'callback':
            return [AllowAny()]  # درگاه callback میده
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]  # همه می‌تونن درگاه‌ها رو ببینن
        return [IsAuthenticated()]

    # ==================== Payment Actions ====================

    @action(detail=False, methods=['post'])
    def pay(self, request):
        """
        ایجاد پرداخت جدید و ریدایرکت به درگاه

        Body:
        {
            "amount": 500000,
            "description": "شارژ کیف پول",
            "gateway_id": "uuid",          // اختیاری - default استفاده میشه
            "invoice_id": "uuid",          // اختیاری
            "callback_url": "https://...", // اختیاری
        }

        Response:
        {
            "success": true,
            "payment_url": "https://api.payping.ir/v2/pay/goto/xxx",
            "payment_log_id": "uuid",
            "gateway_code": "xxx"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            # انتخاب درگاه
            gateway = None
            if data.get('gateway_id'):
                try:
                    gateway = PaymentGateway.objects.get(
                        id=data['gateway_id'],
                        is_active=True
                    )
                except PaymentGateway.DoesNotExist:
                    return Response(
                        {'error': _('Gateway not found or inactive.')},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # دریافت فاکتور
            invoice = None
            if data.get('invoice_id'):
                from apps.financial.models import Invoice
                try:
                    invoice = Invoice.objects.get(
                        id=data['invoice_id'],
                        user=request.user,
                    )
                except Invoice.DoesNotExist:
                    return Response(
                        {'error': _('Invoice not found.')},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # ایجاد پرداخت
            result = PaymentService.create_payment(
                user=request.user,
                amount=data['amount'],
                description=data.get('description', ''),
                invoice=invoice,
                gateway_config=gateway,
                callback_url=data.get('callback_url'),
                request=request,
            )

            if result['success']:
                logger.info(
                    f"Payment created: {result['payment_log'].id} "
                    f"for {request.user.email or request.user.mobile}"
                )

                return Response({
                    'success': True,
                    'message': _('Payment created. Redirect to payment URL.'),
                    'payment_url': result['payment_url'],
                    'payment_log_id': str(result['payment_log'].id),
                    'gateway_code': result['gateway_code'],
                }, status=status.HTTP_201_CREATED)

            return Response({
                'success': False,
                'error': result.get('error', _('Payment creation failed.')),
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Payment creation error: {str(e)}")
            return Response(
                {'error': _('Internal payment error.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get', 'post'], url_path='callback/(?P<payment_log_id>[^/.]+)')
    def callback(self, request, payment_log_id=None):
        """
        Callback از درگاه پرداخت

        PayPing پارامترها رو به صورت GET می‌فرسته:
        ?refid=xxx&clientrefid=xxx

        یا POST:
        {
            "refid": "xxx",
            "clientrefid": "xxx"
        }
        """
        # دریافت داده‌های callback
        callback_data = {}

        if request.method == 'GET':
            callback_data = {
                'refid': request.GET.get('refid', ''),
                'clientrefid': request.GET.get('clientrefid', ''),
                'status': request.GET.get('status', ''),
            }
        else:
            callback_data = request.data or {}

        logger.info(f"Payment callback received: {payment_log_id} - {callback_data}")

        try:
            # تایید پرداخت
            result = PaymentService.verify_payment(
                payment_log_id=payment_log_id,
                callback_data=callback_data,
            )

            if result.get('success'):
                logger.info(f"Payment verified: {payment_log_id}")

                # اگر already_verified بود
                if result.get('already_verified'):
                    return Response({
                        'success': True,
                        'message': _('Payment was already verified.'),
                        'payment_log_id': payment_log_id,
                        'reference_code': result.get('reference_code'),
                    })

                return Response({
                    'success': True,
                    'message': _('Payment verified successfully.'),
                    'payment_log_id': payment_log_id,
                    'reference_code': result.get('reference_code'),
                })

            return Response({
                'success': False,
                'error': result.get('error', _('Payment verification failed.')),
                'payment_log_id': payment_log_id,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Callback error: {str(e)}")
            return Response(
                {'error': _('Callback processing error.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='verify/(?P<payment_log_id>[^/.]+)')
    def verify(self, request, payment_log_id=None):
        """
        تایید دستی پرداخت (ادمین یا کاربر)

        برای مواقعی که callback fail میشه
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = PaymentService.verify_payment(
                payment_log_id=payment_log_id,
                callback_data=serializer.validated_data,
            )

            if result['success']:
                return Response({
                    'success': True,
                    'message': _('Payment verified.'),
                    'reference_code': result.get('reference_code'),
                })

            return Response({
                'success': False,
                'error': result.get('error', _('Verification failed.')),
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Manual verify error: {str(e)}")
            return Response(
                {'error': _('Verification error.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='status/(?P<payment_log_id>[^/.]+)')
    def payment_status(self, request, payment_log_id=None):
        """
        دریافت وضعیت پرداخت

        کاربر می‌تونه وضعیت پرداخت خودش رو چک کنه
        """
        try:
            payment_log = PaymentLog.objects.get(
                id=payment_log_id,
                user=request.user,
            )

            return Response({
                'payment_log_id': str(payment_log.id),
                'amount': float(payment_log.amount),
                'status': payment_log.status,
                'status_display': payment_log.get_status_display(),
                'gateway': payment_log.gateway.name if payment_log.gateway else '-',
                'gateway_code': payment_log.gateway_code,
                'reference_code': payment_log.reference_code,
                'description': payment_log.description,
                'is_verified': payment_log.is_verified,
                'created_at': payment_log.created_at.isoformat(),
                'verified_at': payment_log.verified_at.isoformat() if payment_log.verified_at else None,
            })

        except PaymentLog.DoesNotExist:
            return Response(
                {'error': _('Payment not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """
        لیست پرداخت‌های کاربر جاری

        Query params:
        - status: pending/verified/failed
        - from_date: YYYY-MM-DD
        - to_date: YYYY-MM-DD
        """
        from django.db import models as db_models

        payments = PaymentLog.objects.filter(user=request.user)

        # فیلتر وضعیت
        status_filter = request.query_params.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)

        # فیلتر تاریخ
        from_date = request.query_params.get('from_date')
        if from_date:
            payments = payments.filter(created_at__date__gte=from_date)

        to_date = request.query_params.get('to_date')
        if to_date:
            payments = payments.filter(created_at__date__lte=to_date)

        payments = payments.order_by('-created_at')

        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = PaymentLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PaymentLogSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active_gateways(self, request):
        """
        لیست درگاه‌های فعال (برای frontend)

        کاربر می‌بینه چه درگاه‌هایی در دسترسه
        """
        gateways = PaymentGateway.objects.filter(is_active=True)

        data = []
        for gw in gateways:
            data.append({
                'id': str(gw.id),
                'name': gw.name,
                'type': gw.gateway_type,
                'type_display': gw.get_gateway_type_display(),
                'is_default': gw.is_default,
                'min_amount': float(gw.min_amount),
                'max_amount': float(gw.max_amount),
                'supports': {
                    'crypto': gw.is_crypto,
                    'card_to_card': gw.gateway_type == 'card_to_card',
                    'online': gw.gateway_type in ['payping', 'zarinpal'],
                }
            })

        return Response(data)

    @action(detail=False, methods=['post'])
    def pay_with_wallet(self, request):
        """
        پرداخت مستقیم با کیف پول (بدون درگاه)

        Body:
        {
            "amount": 500000,
            "invoice_id": "uuid",  // اختیاری
            "description": "..."
        }
        """
        amount = request.data.get('amount')
        invoice_id = request.data.get('invoice_id')
        description = request.data.get('description', 'Wallet payment')

        if not amount:
            return Response(
                {'error': _('Amount is required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)

            if not hasattr(request.user, 'wallet'):
                return Response(
                    {'error': _('Wallet not found.')},
                    status=status.HTTP_400_BAD_REQUEST
                )

            wallet = request.user.wallet

            if wallet.available_balance < amount:
                return Response({
                    'error': _('Insufficient wallet balance.'),
                    'available': float(wallet.available_balance),
                    'required': amount,
                }, status=status.HTTP_400_BAD_REQUEST)

            # برداشت از والت
            from apps.financial.services.invoice_service import InvoiceService
            from apps.financial.enums import PaymentMethod

            invoice = None
            if invoice_id:
                from apps.financial.models import Invoice
                try:
                    invoice = Invoice.objects.get(id=invoice_id, user=request.user)
                except Invoice.DoesNotExist:
                    pass

            # برداشت و ثبت
            wallet.withdraw(amount)

            # ایجاد تراکنش
            from apps.financial.models import FinancialTransaction
            from apps.financial.enums import TransactionType, PaymentStatus as FinPaymentStatus

            transaction_obj = FinancialTransaction.objects.create(
                user=request.user,
                invoice=invoice,
                wallet=wallet,
                transaction_type=TransactionType.PAYMENT,
                amount=amount,
                status=FinPaymentStatus.VERIFIED,
                payment_method=PaymentMethod.WALLET,
                reference_code=f"WALLET-DIRECT-{request.user.id}",
                description=description,
                verified_at=__import__('django').utils.timezone.now(),
            )

            logger.info(
                f"Wallet payment: {request.user.email} - {amount:,} Rials"
            )

            return Response({
                'success': True,
                'message': _('Payment successful from wallet.'),
                'amount': amount,
                'transaction_number': transaction_obj.transaction_number,
                'new_balance': float(wallet.balance),
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Wallet payment error: {str(e)}")
            return Response(
                {'error': _('Payment failed.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )