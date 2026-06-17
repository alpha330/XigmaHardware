from django.db import transaction
from django.utils import timezone
from apps.accounts.enums import WalletTransactionType, WalletTransactionStatus
from apps.accounts.models import Wallet, WalletTransaction
from decimal import Decimal


class WalletService:
    """
    سرویس مدیریت کیف پول
    """

    @staticmethod
    @transaction.atomic
    def deposit(wallet, amount, description='', reference_id='', metadata=None):
        """
        افزایش موجودی کیف پول
        """
        if amount <= 0:
            raise ValueError('Amount must be positive')

        # ایجاد تراکنش
        transaction_obj = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=WalletTransactionType.DEPOSIT,
            amount=Decimal(str(amount)),
            status=WalletTransactionStatus.COMPLETED,
            balance_before=wallet.balance,
            description=description,
            reference_id=reference_id,
            metadata=metadata or {},
            completed_at=timezone.now()
        )

        # افزایش موجودی
        wallet.deposit(amount)
        transaction_obj.balance_after = wallet.balance
        transaction_obj.save(update_fields=['balance_after'])

        return transaction_obj

    @staticmethod
    @transaction.atomic
    def withdraw(wallet, amount, description='', reference_id='', metadata=None):
        """
        برداشت از کیف پول
        """
        if amount <= 0:
            raise ValueError('Amount must be positive')

        if amount > wallet.available_balance:
            raise ValueError('Insufficient balance')

        # ایجاد تراکنش
        transaction_obj = WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type=WalletTransactionType.WITHDRAW,
            amount=Decimal(str(amount)),
            status=WalletTransactionStatus.COMPLETED,
            balance_before=wallet.balance,
            description=description,
            reference_id=str(reference_id) if reference_id else None,
            metadata=metadata or {},
            completed_at=timezone.now()
        )

        # کاهش موجودی
        wallet.withdraw(amount)
        transaction_obj.balance_after = wallet.balance
        transaction_obj.save(update_fields=['balance_after'])

        return transaction_obj

    @staticmethod
    @transaction.atomic
    def transfer(from_wallet, to_wallet, amount, description='', reference_id=''):
        """
        انتقال وجه بین دو کیف پول
        """
        if amount <= 0:
            raise ValueError('Amount must be positive')

        if amount > from_wallet.available_balance:
            raise ValueError('Insufficient balance')

        # برداشت از مبدا
        withdraw_tx = WalletService.withdraw(
            from_wallet,
            amount=Decimal(str(amount)),
            description=f'Transfer to {to_wallet.user.get_display_name()} - {description}',
            reference_id=reference_id
        )

        # واریز به مقصد
        deposit_tx = WalletService.deposit(
            to_wallet,
            amount=Decimal(str(amount)),
            description=f'Transfer from {from_wallet.user.get_display_name()} - {description}',
            reference_id=reference_id
        )

        return withdraw_tx, deposit_tx

    @staticmethod
    def get_balance(wallet):
        """دریافت موجودی کیف پول"""
        return {
            'balance': float(wallet.balance),
            'blocked_balance': float(wallet.blocked_balance),
            'available_balance': float(wallet.available_balance),
        }

    @staticmethod
    def get_transactions(wallet, transaction_type=None, status=None, limit=50):
        """دریافت لیست تراکنش‌ها"""
        queryset = wallet.transactions.all()

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        if status:
            queryset = queryset.filter(status=status)

        return queryset[:limit]