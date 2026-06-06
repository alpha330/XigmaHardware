import logging
from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.financial.models import FinancialTransaction
from apps.financial.enums import TransactionType, PaymentStatus, PaymentMethod
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class TransactionService:
    """
    سرویس مدیریت تراکنش‌های مالی

    عملیات‌های اصلی:
    - ثبت تراکنش
    - تایید پرداخت
    - ابطال تراکنش
    - استعلام وضعیت
    """

    @classmethod
    @db_transaction.atomic
    def create_transaction(cls, user, amount, transaction_type, payment_method=None,
                           invoice=None, wallet=None, reference_code='',
                           description='', status=PaymentStatus.PENDING):
        """
        ایجاد تراکنش جدید

        Args:
            user: کاربر
            amount: مبلغ
            transaction_type: نوع تراکنش
            payment_method: روش پرداخت
            invoice: فاکتور مرتبط
            wallet: والت مرتبط
            reference_code: کد پیگیری
            description: توضیحات
            status: وضعیت اولیه

        Returns:
            FinancialTransaction
        """
        if amount <= 0:
            raise ValueError(_('Amount must be positive.'))

        transaction_obj = FinancialTransaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount=amount,
            status=status,
            payment_method=payment_method,
            invoice=invoice,
            wallet=wallet,
            reference_code=reference_code,
            description=description,
            transaction_date=timezone.now(),
        )

        logger.info(
            f"Transaction {transaction_obj.transaction_number} created: "
            f"{transaction_type} {amount:,} for {user.get_display_name()}"
        )

        return transaction_obj

    @classmethod
    @db_transaction.atomic
    def verify_payment(cls, transaction_obj, reference_code='',
                       payment_method=None, verified_by=None, notes=''):
        """
        تایید پرداخت

        Args:
            transaction_obj: تراکنش
            reference_code: کد پیگیری بانک
            payment_method: روش پرداخت
            verified_by: تایید کننده
            notes: یادداشت

        Returns:
            FinancialTransaction
        """
        if transaction_obj.is_verified:
            raise ValueError(_('Transaction already verified.'))

        if transaction_obj.status == PaymentStatus.FAILED:
            raise ValueError(_('Cannot verify a failed transaction.'))

        # بروزرسانی تراکنش
        transaction_obj.status = PaymentStatus.VERIFIED
        transaction_obj.reference_code = reference_code
        transaction_obj.verified_at = timezone.now()
        transaction_obj.verified_by = verified_by

        if payment_method:
            transaction_obj.payment_method = payment_method

        if notes:
            transaction_obj.description = (
                f"{transaction_obj.description}\nNote: {notes}"
            )

        transaction_obj.save()

        # اگر فاکتور داره و فاکتور شارژ والت هست
        if transaction_obj.invoice and transaction_obj.invoice.is_wallet_charge:
            from .invoice_service import InvoiceService
            InvoiceService.process_wallet_charge(
                invoice=transaction_obj.invoice,
                verified_by=verified_by,
            )

        # اگر فاکتور داره و پرداخت فاکتور هست
        elif transaction_obj.invoice and transaction_obj.transaction_type == TransactionType.PAYMENT:
            transaction_obj.invoice.add_payment(transaction_obj.amount)

        logger.info(
            f"Transaction {transaction_obj.transaction_number} verified "
            f"by {verified_by.get_display_name() if verified_by else 'system'}"
        )

        return transaction_obj

    @classmethod
    @db_transaction.atomic
    def fail_transaction(cls, transaction_obj, reason=''):
        """
        ابطال/ناموفق کردن تراکنش

        Args:
            transaction_obj: تراکنش
            reason: دلیل

        Returns:
            FinancialTransaction
        """
        if transaction_obj.is_verified:
            raise ValueError(_('Cannot fail a verified transaction.'))

        transaction_obj.fail(reason)

        logger.info(f"Transaction {transaction_obj.transaction_number} failed: {reason}")

        return transaction_obj

    @classmethod
    @db_transaction.atomic
    def refund_transaction(cls, transaction_obj, refund_amount=None, reason=''):
        """
        برگشت تراکنش

        Args:
            transaction_obj: تراکنش اصلی
            refund_amount: مبلغ برگشتی (None = کل مبلغ)
            reason: دلیل برگشت

        Returns:
            FinancialTransaction: تراکنش برگشتی
        """
        if not transaction_obj.is_verified:
            raise ValueError(_('Only verified transactions can be refunded.'))

        refund_amount = refund_amount or transaction_obj.amount

        # ایجاد تراکنش برگشتی
        refund_transaction = FinancialTransaction.objects.create(
            user=transaction_obj.user,
            invoice=transaction_obj.invoice,
            wallet=transaction_obj.wallet,
            transaction_type=TransactionType.REFUND,
            amount=refund_amount,
            status=PaymentStatus.VERIFIED,
            payment_method=transaction_obj.payment_method,
            reference_code=f"REFUND-{transaction_obj.transaction_number}",
            description=f"Refund for {transaction_obj.transaction_number}: {reason}",
            verified_at=timezone.now(),
        )

        # اگر والت داره، برگشت به والت
        if transaction_obj.wallet and transaction_obj.transaction_type == TransactionType.PAYMENT:
            transaction_obj.wallet.deposit(refund_amount)

        # علامت‌گذاری تراکنش اصلی
        transaction_obj.status = PaymentStatus.REFUNDED
        transaction_obj.save()

        logger.info(
            f"Refund {refund_amount:,} for transaction "
            f"{transaction_obj.transaction_number}"
        )

        return refund_transaction

    @classmethod
    def get_user_transactions(cls, user, transaction_type=None, status=None, limit=50):
        """
        دریافت تراکنش‌های کاربر

        Args:
            user: کاربر
            transaction_type: نوع تراکنش
            status: وضعیت
            limit: تعداد

        Returns:
            QuerySet
        """
        queryset = FinancialTransaction.objects.filter(user=user)

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-transaction_date')[:limit]

    @classmethod
    def get_pending_transactions(cls):
        """
        تراکنش‌های در انتظار تایید

        Returns:
            QuerySet
        """
        return FinancialTransaction.objects.filter(
            status=PaymentStatus.PENDING
        ).order_by('-transaction_date')

    @classmethod
    def get_daily_stats(cls, date=None):
        """
        آمار تراکنش‌های روزانه

        Args:
            date: تاریخ (پیش‌فرض امروز)

        Returns:
            dict
        """
        from django.db.models import Sum, Count

        if not date:
            date = timezone.now().date()

        transactions = FinancialTransaction.objects.filter(
            transaction_date__date=date
        )

        return {
            'date': date.isoformat(),
            'total_count': transactions.count(),
            'total_amount': float(transactions.aggregate(Sum('amount'))['amount__sum'] or 0),
            'verified_count': transactions.filter(status='verified').count(),
            'verified_amount': float(
                transactions.filter(status='verified').aggregate(Sum('amount'))['amount__sum'] or 0
            ),
            'pending_count': transactions.filter(status='pending').count(),
            'failed_count': transactions.filter(status='failed').count(),
            'by_type': {
                t: transactions.filter(transaction_type=t).count()
                for t in ['payment', 'deposit', 'withdraw', 'refund', 'wallet_charge']
            },
            'by_method': {
                m: transactions.filter(payment_method=m).count()
                for m in ['wallet', 'card_to_card', 'bank_transfer', 'online_gateway']
                if transactions.filter(payment_method=m).exists()
            },
        }