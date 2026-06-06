import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.financial.enums import InvoiceType, InvoiceStatus, PaymentMethod


class Invoice(models.Model):
    """
    مدل پیش‌فاکتور و فاکتور

    انواع:
    - PROFORMA: پیش‌فاکتور (قابل ویرایش)
    - FINAL: فاکتور نهایی (بعد از پرداخت)
    - WALLET_CHARGE: فاکتور شارژ کیف پول
    - REFUND: فاکتور برگشتی
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Basic Info ====================
    invoice_number = models.CharField(
        _('Invoice Number'),
        max_length=30,
        unique=True,
        db_index=True,
        help_text=_('Format: INV-YYYYMMDD-XXXXXX')
    )

    invoice_type = models.CharField(
        _('Type'),
        max_length=15,
        choices=InvoiceType.choices,
        default=InvoiceType.PROFORMA,
        db_index=True
    )

    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        db_index=True
    )

    # ==================== Relations ====================
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoices',
        verbose_name=_('Customer')
    )

    # ارتباط با Cart (اختیاری)
    cart = models.ForeignKey(
        'basket.Cart',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Related Cart')
    )

    # ارتباط با فاکتور اصلی (برای فاکتورهای برگشتی)
    related_invoice = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds',
        verbose_name=_('Related Invoice')
    )

    # ==================== Pricing ====================
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    discount_amount = models.DecimalField(
        _('Discount'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    tax_amount = models.DecimalField(
        _('Tax (VAT)'),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_('Value Added Tax')
    )

    shipping_amount = models.DecimalField(
        _('Shipping'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        _('Total'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    paid_amount = models.DecimalField(
        _('Paid'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    remaining_amount = models.DecimalField(
        _('Remaining'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    # ==================== Currency ====================
    currency = models.CharField(
        _('Currency'),
        max_length=3,
        default='IRR',
        help_text=_('IRR, USD, EUR')
    )

    # ==================== Payment ====================
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )

    payment_due_date = models.DateField(
        _('Payment Due Date'),
        null=True,
        blank=True
    )

    paid_at = models.DateTimeField(
        _('Paid At'),
        null=True,
        blank=True
    )

    # ==================== Billing Info ====================
    billing_name = models.CharField(
        _('Billing Name'),
        max_length=200,
        blank=True
    )

    billing_company = models.CharField(
        _('Company'),
        max_length=200,
        blank=True
    )

    billing_national_id = models.CharField(
        _('National ID'),
        max_length=11,
        blank=True
    )

    billing_economic_code = models.CharField(
        _('Economic Code'),
        max_length=12,
        blank=True
    )

    billing_address = models.TextField(
        _('Billing Address'),
        blank=True
    )

    billing_postal_code = models.CharField(
        _('Postal Code'),
        max_length=10,
        blank=True
    )

    billing_phone = models.CharField(
        _('Phone'),
        max_length=15,
        blank=True
    )

    # ==================== Notes ====================
    notes = models.TextField(_('Internal Notes'), blank=True)
    customer_notes = models.TextField(_('Customer Notes'), blank=True)

    # ==================== Approval ====================
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        verbose_name=_('Created By')
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_invoices',
        verbose_name=_('Approved By')
    )

    approved_at = models.DateTimeField(
        _('Approved At'),
        null=True,
        blank=True
    )

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    expires_at = models.DateTimeField(
        _('Expires At'),
        null=True,
        blank=True,
        help_text=_('Proforma expiry date')
    )

    class Meta:
        db_table = 'invoices'
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['user', 'invoice_type', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['payment_due_date']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.user.get_display_name() if self.user else 'N/A'}"

    # ==================== Properties ====================
    @property
    def is_proforma(self):
        return self.invoice_type == InvoiceType.PROFORMA

    @property
    def is_final(self):
        return self.invoice_type == InvoiceType.FINAL

    @property
    def is_wallet_charge(self):
        return self.invoice_type == InvoiceType.WALLET_CHARGE

    @property
    def is_paid(self):
        return self.status == InvoiceStatus.PAID

    @property
    def is_fully_paid(self):
        return self.paid_amount >= self.total_amount

    @property
    def balance(self):
        """مانده قابل پرداخت"""
        return max(0, self.total_amount - self.paid_amount)

    @property
    def items_count(self):
        return self.items.count()

    @property
    def payments_count(self):
        return self.payments.count()

    # ==================== Methods ====================
    def calculate_totals(self):
        """محاسبه مجدد مبالغ"""
        items_total = sum(item.total_price for item in self.items.all())

        self.subtotal = items_total
        self.tax_amount = self.subtotal * Decimal('0.09')  # VAT 9%
        self.total_amount = (
            self.subtotal
            - self.discount_amount
            + self.tax_amount
            + self.shipping_amount
        )
        self.remaining_amount = max(0, self.total_amount - self.paid_amount)
        self.save()

    def mark_as_paid(self, payment_method=None):
        """علامت‌گذاری به عنوان پرداخت شده"""
        self.status = InvoiceStatus.PAID
        self.paid_amount = self.total_amount
        self.remaining_amount = 0
        self.paid_at = timezone.now()

        if payment_method:
            self.payment_method = payment_method

        self.save()

    def add_payment(self, amount):
        """ثبت پرداخت جزئی"""
        self.paid_amount += amount
        self.remaining_amount = max(0, self.total_amount - self.paid_amount)

        if self.is_fully_paid:
            self.status = InvoiceStatus.PAID
            self.paid_at = timezone.now()
        else:
            self.status = InvoiceStatus.PARTIALLY_PAID

        self.save()

    def convert_to_final(self):
        """تبدیل پیش‌فاکتور به فاکتور نهایی"""
        if not self.is_proforma:
            raise ValueError(_('Only proforma invoices can be converted.'))

        self.invoice_type = InvoiceType.FINAL

        # تولید شماره فاکتور نهایی
        self.invoice_number = self._generate_invoice_number('FINAL')

        self.save()

    def cancel(self, reason=''):
        """لغو فاکتور"""
        self.status = InvoiceStatus.CANCELLED
        self.notes = f"{self.notes}\nCancelled: {reason}" if reason else self.notes
        self.save()

    def _generate_invoice_number(self, prefix='INV'):
        """تولید شماره فاکتور یکتا"""
        from datetime import datetime
        now = datetime.now()
        date_part = now.strftime('%Y%m%d')
        random_part = uuid.uuid4().hex[:6].upper()
        return f"{prefix}-{date_part}-{random_part}"

    def save(self, *args, **kwargs):
        """تولید شماره فاکتور اگر خالی بود"""
        if not self.invoice_number:
            self.invoice_number = self._generate_invoice_number()
        super().save(*args, **kwargs)