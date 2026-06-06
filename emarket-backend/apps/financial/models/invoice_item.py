import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _


class InvoiceItem(models.Model):
    """
    اقلام فاکتور
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Relations ====================
    invoice = models.ForeignKey(
        'financial.Invoice',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Invoice')
    )

    # محصول (اختیاری - برای فاکتورهای غیرمحصولی مثل شارژ والت)
    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_items',
        verbose_name=_('Product')
    )

    # ==================== Item Info ====================
    description = models.CharField(
        _('Description'),
        max_length=500
    )

    sku = models.CharField(
        _('SKU'),
        max_length=50,
        blank=True
    )

    # ==================== Quantity & Price ====================
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        default=1
    )

    unit_price = models.DecimalField(
        _('Unit Price'),
        max_digits=15,
        decimal_places=2
    )

    discount_percent = models.DecimalField(
        _('Discount %'),
        max_digits=5,
        decimal_places=2,
        default=0
    )

    tax_percent = models.DecimalField(
        _('Tax %'),
        max_digits=5,
        decimal_places=2,
        default=9,
        help_text=_('VAT percentage')
    )

    # ==================== Calculated ====================
    total_price = models.DecimalField(
        _('Total Price'),
        max_digits=15,
        decimal_places=2,
        editable=False,
        help_text=_('quantity * unit_price - discount')
    )

    # ==================== Warranty ====================
    warranty_description = models.CharField(
        _('Warranty'),
        max_length=300,
        blank=True
    )

    # ==================== Notes ====================
    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoice_items'
        verbose_name = _('Invoice Item')
        verbose_name_plural = _('Invoice Items')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.description} x{self.quantity} - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        """محاسبه خودکار قیمت کل"""
        self.total_price = (
            self.unit_price * self.quantity
            * (1 - self.discount_percent / 100)
        )
        super().save(*args, **kwargs)