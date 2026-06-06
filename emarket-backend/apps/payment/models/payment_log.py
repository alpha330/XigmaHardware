import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.payment.enums import PaymentStatus


class PaymentLog(models.Model):
    """
    لاگ تمام تراکنش‌های پرداخت

    هر پرداخت از طریق درگاه اینجا ثبت میشه
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
        related_name='payment_logs',
        verbose_name=_('User')
    )

    gateway = models.ForeignKey(
        'payment.PaymentGateway',
        on_delete=models.SET_NULL,
        null=True,
        related_name='payment_logs',
        verbose_name=_('Gateway')
    )

    invoice = models.ForeignKey(
        'financial.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_logs',
        verbose_name=_('Invoice')
    )

    transaction = models.ForeignKey(
        'financial.FinancialTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_logs',
        verbose_name=_('Transaction')
    )

    # ==================== Payment Info ====================
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

    # ==================== Gateway Response ====================
    gateway_code = models.CharField(
        _('Gateway Payment Code'),
        max_length=200,
        blank=True,
        help_text=_('Payment code/ID from gateway (e.g., payping code)')
    )

    reference_code = models.CharField(
        _('Reference Code'),
        max_length=200,
        blank=True,
        help_text=_('Bank reference number')
    )

    gateway_request = models.JSONField(
        _('Request Data'),
        default=dict,
        blank=True
    )

    gateway_response = models.JSONField(
        _('Response Data'),
        default=dict,
        blank=True
    )

    callback_data = models.JSONField(
        _('Callback Data'),
        default=dict,
        blank=True
    )

    # ==================== Description ====================
    description = models.CharField(
        _('Description'),
        max_length=500,
        blank=True
    )

    payer_ip = models.GenericIPAddressField(
        _('Payer IP'),
        null=True,
        blank=True
    )

    # ==================== Timestamps ====================
    payment_date = models.DateTimeField(
        _('Payment Date'),
        default=timezone.now,
        db_index=True
    )

    verified_at = models.DateTimeField(
        _('Verified At'),
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_logs'
        verbose_name = _('Payment Log')
        verbose_name_plural = _('Payment Logs')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['gateway', 'status']),
            models.Index(fields=['gateway_code']),
            models.Index(fields=['reference_code']),
        ]

    def __str__(self):
        return f"Payment {self.id[:8]}: {self.amount:,} Rials - {self.get_status_display()}"

    @property
    def is_verified(self):
        return self.status == PaymentStatus.VERIFIED

    def mark_redirected(self, gateway_code):
        """علامت‌گذاری بعد از ریدایرکت به درگاه"""
        self.status = PaymentStatus.REDIRECTED
        self.gateway_code = gateway_code
        self.save()

    def mark_verified(self, reference_code):
        """علامت‌گذاری بعد از تایید پرداخت"""
        self.status = PaymentStatus.VERIFIED
        self.reference_code = reference_code
        self.verified_at = timezone.now()
        self.save()

    def mark_failed(self, reason=''):
        """علامت‌گذاری پرداخت ناموفق"""
        self.status = PaymentStatus.FAILED
        self.description = f"{self.description}\nFailed: {reason}" if reason else self.description
        self.save()