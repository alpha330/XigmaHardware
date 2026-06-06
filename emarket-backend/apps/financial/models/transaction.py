import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.financial.enums import TransactionType, PaymentStatus, PaymentMethod


class FinancialTransaction(models.Model):
    """
    تراکنش‌های مالی

    هر پرداخت، واریز، برداشت یا برگشتی
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Relations ====================
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='financial_transactions',
        verbose_name=_('User')
    )

    invoice = models.ForeignKey(
        'financial.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('Invoice')
    )

    wallet = models.ForeignKey(
        'accounts.Wallet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_transactions',
        verbose_name=_('Wallet')
    )

    # ==================== Transaction Info ====================
    transaction_number = models.CharField(
        _('Transaction Number'),
        max_length=30,
        unique=True,
        db_index=True,
        help_text=_('TRX-YYYYMMDD-XXXXXX')
    )

    transaction_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=TransactionType.choices,
        db_index=True
    )

    amount = models.DecimalField(
        _('Amount'),
        max_digits=15,
        decimal_places=2
    )

    status = models.CharField(
        _('Status'),
        max_length=15,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True
    )

    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )

    # ==================== Tracking ====================
    reference_code = models.CharField(
        _('Reference Code'),
        max_length=100,
        blank=True,
        help_text=_('Bank reference or gateway tracking code')
    )

    gateway_response = models.JSONField(
        _('Gateway Response'),
        default=dict,
        blank=True
    )

    # ==================== Description ====================
    description = models.TextField(_('Description'), blank=True)

    # ==================== Dates ====================
    transaction_date = models.DateTimeField(
        _('Transaction Date'),
        default=timezone.now,
        db_index=True
    )

    verified_at = models.DateTimeField(
        _('Verified At'),
        null=True,
        blank=True
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_transactions',
        verbose_name=_('Verified By')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_transactions'
        verbose_name = _('Financial Transaction')
        verbose_name_plural = _('Financial Transactions')
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_number']),
            models.Index(fields=['user', 'transaction_type', 'status']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['invoice', 'status']),
        ]

    def __str__(self):
        return f"{self.transaction_number} - {self.get_transaction_type_display()}: {self.amount:,}"

    @property
    def is_verified(self):
        return self.status == PaymentStatus.VERIFIED

    @property
    def is_pending(self):
        return self.status == PaymentStatus.PENDING

    def verify(self, verified_by=None):
        """تایید تراکنش"""
        self.status = PaymentStatus.VERIFIED
        self.verified_at = timezone.now()
        self.verified_by = verified_by
        self.save()

    def fail(self, reason=''):
        """ناموفق"""
        self.status = PaymentStatus.FAILED
        self.description = f"{self.description}\nFailed: {reason}" if reason else self.description
        self.save()

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            self.transaction_number = self._generate_number()
        super().save(*args, **kwargs)

    def _generate_number(self):
        from datetime import datetime
        date_part = datetime.now().strftime('%Y%m%d')
        random_part = uuid.uuid4().hex[:6].upper()
        return f"TRX-{date_part}-{random_part}"