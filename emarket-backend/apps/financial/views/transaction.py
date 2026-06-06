import logging
from django.db import models as db_models
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.financial.models import FinancialTransaction
from apps.financial.serializers.transaction import (
    TransactionSerializer,
    TransactionListSerializer,
    PaymentVerificationSerializer,
)
from apps.financial.permissions import CanManageFinancial, CanVerifyPayment, CanViewOwnInvoices
from apps.financial.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class TransactionViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    ViewSet مشاهده تراکنش‌های مالی (فقط خواندنی)

    تراکنش‌ها از طریق:
    - پرداخت فاکتور
    - واریز/برداشت والت
    - سیستم پرداخت خودکار
    """
    queryset = FinancialTransaction.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TransactionListSerializer
        elif self.action == 'verify':
            return PaymentVerificationSerializer
        return TransactionSerializer

    def get_permissions(self):
        if self.action == 'verify':
            return [IsAuthenticated(), CanVerifyPayment()]
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), CanViewOwnInvoices()]
        return [IsAuthenticated(), CanManageFinancial()]

    def get_queryset(self):
        user = self.request.user
        queryset = FinancialTransaction.objects.select_related(
            'user', 'invoice', 'wallet', 'verified_by'
        )

        # کاربران عادی فقط تراکنش‌های خودشون
        if not user.is_superuser and user.role not in ['super_admin', 'accountant']:
            queryset = queryset.filter(user=user)

        # فیلترها
        tx_type = self.request.query_params.get('type')
        if tx_type:
            queryset = queryset.filter(transaction_type=tx_type)

        tx_status = self.request.query_params.get('status')
        if tx_status:
            queryset = queryset.filter(status=tx_status)

        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        from_date = self.request.query_params.get('from_date')
        if from_date:
            queryset = queryset.filter(transaction_date__date__gte=from_date)

        to_date = self.request.query_params.get('to_date')
        if to_date:
            queryset = queryset.filter(transaction_date__date__lte=to_date)

        # جستجو
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                db_models.Q(transaction_number__icontains=search) |
                db_models.Q(reference_code__icontains=search) |
                db_models.Q(description__icontains=search) |
                db_models.Q(user__email__icontains=search)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """تایید پرداخت"""
        transaction = self.get_object()

        if transaction.is_verified:
            return Response({'error': _('Transaction already verified.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            transaction = TransactionService.verify_payment(
                transaction=transaction,
                reference_code=serializer.validated_data['reference_code'],
                payment_method=serializer.validated_data['payment_method'],
                verified_by=request.user,
                notes=serializer.validated_data.get('notes', ''),
            )

            return Response({
                'message': _('Payment verified.'),
                'transaction': TransactionSerializer(transaction, context={'request': request}).data,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """علامت‌گذاری تراکنش ناموفق"""
        transaction = self.get_object()
        reason = request.data.get('reason', 'Unknown')

        transaction.fail(reason)

        return Response({
            'message': _('Transaction marked as failed.'),
            'status': transaction.status,
        })

    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """تراکنش‌های من"""
        transactions = FinancialTransaction.objects.filter(
            user=request.user
        ).order_by('-transaction_date')

        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionListSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار تراکنش‌ها"""
        from django.db.models import Sum, Count

        transactions = FinancialTransaction.objects.all()

        if not request.user.is_superuser and request.user.role not in ['super_admin', 'accountant']:
            transactions = transactions.filter(user=request.user)

        stats = {
            'total_transactions': transactions.count(),
            'total_amount': float(transactions.aggregate(Sum('amount'))['amount__sum'] or 0),
            'verified_amount': float(transactions.filter(status='verified').aggregate(Sum('amount'))['amount__sum'] or 0),
            'pending_amount': float(transactions.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0),
            'by_type': {
                t: transactions.filter(transaction_type=t).count()
                for t in ['payment', 'deposit', 'withdraw', 'refund', 'commission', 'wallet_charge']
            },
            'by_status': {
                s: transactions.filter(status=s).count()
                for s in ['pending', 'verified', 'failed', 'refunded']
            },
            'by_payment_method': {
                m: transactions.filter(payment_method=m).count()
                for m in ['wallet', 'card_to_card', 'bank_transfer', 'online_gateway', 'cash', 'cheque']
                if transactions.filter(payment_method=m).exists()
            },
        }

        return Response(stats)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """تراکنش‌های در انتظار تایید"""
        transactions = FinancialTransaction.objects.filter(
            status='pending'
        ).order_by('-transaction_date')

        serializer = TransactionListSerializer(transactions, many=True)
        return Response(serializer.data)