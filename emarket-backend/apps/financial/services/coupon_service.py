import logging
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from apps.financial.models.coupon import Coupon
from apps.financial.models.invoice import Invoice

logger = logging.getLogger(__name__)


class CouponService:

    @classmethod
    @transaction.atomic
    def apply_coupon(cls, code, invoice_id):
        """اعمال کوپن روی فاکتور"""
        try:
            coupon = Coupon.objects.get(code=code.upper())
        except Coupon.DoesNotExist:
            raise ValueError(_('Invalid coupon code.'))

        try:
            invoice = Invoice.objects.select_for_update().get(id=invoice_id)
        except Invoice.DoesNotExist:
            raise ValueError(_('Invoice not found.'))

        # بررسی وضعیت فاکتور
        if invoice.status not in ['draft', 'pending']:
            raise ValueError(_('Coupon can only be applied to draft/pending invoices.'))

        # بررسی اعتبار کوپن
        valid, msg = coupon.is_valid(invoice.total_amount)
        if not valid:
            raise ValueError(msg)

        # محاسبه تخفیف
        discount = coupon.calculate_discount(invoice.total_amount)

        # اعمال تخفیف روی فاکتور
        invoice.discount_amount += discount
        invoice.total_amount -= discount
        invoice.remaining_amount = max(0, invoice.total_amount - invoice.paid_amount)
        invoice.save()

        # افزایش تعداد استفاده
        coupon.mark_used()

        logger.info(f"Coupon {coupon.code} applied to invoice {invoice.invoice_number}: {discount}")

        return {
            'success': True,
            'message': _('Coupon applied successfully.'),
            'discount_amount': float(discount),
            'new_total': float(invoice.total_amount),
            'coupon_code': coupon.code,
        }