import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.accounts.enums import WalletTransactionType, WalletTransactionStatus
from django.utils import timezone

class Wallet(models.Model):
    """
    مدل کیف پول کاربر
    هر کاربر دقیقاً یک کیف پول دارد
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name=_('User')
    )
    
    balance = models.DecimalField(
        _('Balance'),
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text=_('Current wallet balance in Rials')
    )
    
    blocked_balance = models.DecimalField(
        _('Blocked Balance'),
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text=_('Blocked balance for pending transactions')
    )
    
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        db_index=True
    )
    
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'wallets'
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['balance']),
        ]
    
    def __str__(self):
        return f"Wallet: {self.user.get_display_name()} - {self.available_balance:,} Rials"
    
    @property
    def available_balance(self):
        return self.balance - self.blocked_balance
    
    def deposit(self, amount):
        """افزایش موجودی (امن برای Decimal و float)"""
        amount = Decimal(str(amount))
        if amount > 0:
            self.balance += amount
            self.save(update_fields=['balance', 'updated_at'])
            return True
        return False
    
    def withdraw(self, amount):
        """برداشت از موجودی (امن برای Decimal و float)"""
        amount = Decimal(str(amount))
        if 0 < amount <= self.available_balance:
            self.balance -= amount
            self.save(update_fields=['balance', 'updated_at'])
            return True
        return False
    
    def block_amount(self, amount):
        amount = Decimal(str(amount))
        if 0 < amount <= self.available_balance:
            self.blocked_balance += amount
            self.save(update_fields=['blocked_balance', 'updated_at'])
            return True
        return False
    
    def unblock_amount(self, amount):
        amount = Decimal(str(amount))
        if 0 < amount <= self.blocked_balance:
            self.blocked_balance -= amount
            self.save(update_fields=['blocked_balance', 'updated_at'])
            return True
        return False


class WalletTransaction(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('Wallet')
    )
    
    transaction_type = models.CharField(
        _('Transaction Type'),
        max_length=20,
        choices=WalletTransactionType.choices,
        db_index=True
    )
    
    amount = models.DecimalField(
        _('Amount'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=WalletTransactionStatus.choices,
        default=WalletTransactionStatus.PENDING,
        db_index=True
    )
    
    balance_before = models.DecimalField(
        _('Balance Before'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    balance_after = models.DecimalField(
        _('Balance After'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    description = models.TextField(
        _('Description'),
        blank=True
    )
    
    reference_id = models.CharField(
        _('Reference ID'),
        max_length=100,
        blank=True,
        db_index=True,
        help_text=_('External reference (order ID, payment ID, etc.)')
    )
    
    metadata = models.JSONField(
        _('Metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional transaction data')
    )
    
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True,
        db_index=True
    )
    
    completed_at = models.DateTimeField(
        _('Completed At'),
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'wallet_transactions'
        verbose_name = _('Wallet Transaction')
        verbose_name_plural = _('Wallet Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'transaction_type', 'status']),
            models.Index(fields=['reference_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.amount:,} Rials - {self.status}"
    
    def complete(self):
        if self.status == WalletTransactionStatus.PENDING:
            self.status = WalletTransactionStatus.COMPLETED
            self.completed_at = timezone.now()
            self.save(update_fields=['status', 'completed_at'])
    
    def cancel(self):
        if self.status == WalletTransactionStatus.PENDING:
            self.status = WalletTransactionStatus.CANCELLED
            self.save(update_fields=['status'])
    
    def fail(self, reason=''):
        if self.status == WalletTransactionStatus.PENDING:
            self.status = WalletTransactionStatus.FAILED
            if reason:
                self.description = f"{self.description}\nReason: {reason}"
            self.save(update_fields=['status', 'description'])