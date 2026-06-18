import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.financial.models import Invoice, InvoiceItem, FinancialTransaction
from apps.financial.enums import (
    InvoiceType, InvoiceStatus, PaymentMethod,
    TransactionType, PaymentStatus,
)
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class InvoiceService:
    """
    سرویس مدیریت فاکتورها

    عملیات‌های اصلی:
    - ایجاد فاکتور (دستی، از Cart، شارژ والت)
    - تبدیل پیش‌فاکتور به فاکتور نهایی
    - ثبت پرداخت
    - پرداخت با والت
    - محاسبه مالیات و تخفیف
    - لغو/ابطال فاکتور
    """

    # ==================== Create Invoice ====================

    @classmethod
    @transaction.atomic
    def create_invoice(cls, user, invoice_type='proforma', items_data=None,
                       discount_amount=0, tax_percent=9, shipping_amount=0,
                       payment_due_date=None, notes='', customer_notes='',
                       billing_info=None, created_by=None):
        """
        ایجاد فاکتور جدید

        Args:
            user: کاربر
            invoice_type: نوع فاکتور
            items_data: لیست آیتم‌ها
            discount_amount: تخفیف کل
            tax_percent: درصد مالیات
            shipping_amount: هزینه ارسال
            payment_due_date: مهلت پرداخت
            notes: یادداشت داخلی
            customer_notes: یادداشت مشتری
            billing_info: اطلاعات صورتحساب
            created_by: ایجاد کننده

        Returns:
            Invoice
        """
        if not items_data:
            raise ValueError(_('At least one item is required.'))

        # ایجاد فاکتور
        invoice = Invoice.objects.create(
            user=user,
            invoice_type=invoice_type,
            status=InvoiceStatus.DRAFT,
            discount_amount=discount_amount,
            shipping_amount=shipping_amount,
            payment_due_date=payment_due_date or (timezone.now() + timezone.timedelta(days=7)).date(),
            notes=notes,
            customer_notes=customer_notes,
            created_by=created_by,
            **cls._prepare_billing_info(billing_info),
        )

        # افزودن آیتم‌ها
        for item_data in items_data:
            InvoiceItem.objects.create(
                invoice=invoice,
                product=item_data.get('product'),
                description=item_data.get('description', ''),
                sku=item_data.get('sku', ''),
                quantity=item_data.get('quantity', 1),
                unit_price=item_data.get('unit_price', 0),
                discount_percent=item_data.get('discount_percent', 0),
                tax_percent=item_data.get('tax_percent', tax_percent),
                warranty_description=item_data.get('warranty_description', ''),
                notes=item_data.get('notes', ''),
            )

        # محاسبه مبالغ
        invoice.calculate_totals()

        logger.info(
            f"Invoice {invoice.invoice_number} created for "
            f"{user.get_display_name()} with {invoice.items_count} items"
        )

        return invoice

    @classmethod
    @transaction.atomic
    def create_from_cart(cls, cart, payment_method='wallet', notes='', created_by=None):
        """
        ایجاد فاکتور از سبد خرید (Cart)

        Args:
            cart: سبد خرید
            payment_method: روش پرداخت
            notes: یادداشت
            created_by: ایجاد کننده

        Returns:
            Invoice
        """
        if not cart.items.filter(is_active=True).exists():
            raise ValueError(_('Cart is empty.'))

        # دریافت اطلاعات کاربر از پروفایل
        user = cart.user
        billing_info = {}

        if hasattr(user, 'profile'):
            profile = user.profile
            billing_info = {
                'name': user.get_full_name(),
                'company': profile.company_name if profile.is_legal else '',
                'national_id': profile.national_id if profile.is_legal else profile.national_code,
                'economic_code': profile.economic_code if profile.is_legal else '',
                'address': profile.address,
                'postal_code': profile.postal_code,
                'phone': user.mobile or profile.tel or '',
            }

        # ایجاد فاکتور
        invoice = Invoice.objects.create(
            user=user,
            cart=cart,
            invoice_type=InvoiceType.FINAL,
            status=InvoiceStatus.PENDING,
            payment_method=payment_method,
            discount_amount=cart.discount_total,
            payment_due_date=(timezone.now() + timezone.timedelta(days=3)).date(),
            notes=notes,
            created_by=created_by,
            **cls._prepare_billing_info(billing_info),
        )

        # انتقال آیتم‌ها از Cart
        for cart_item in cart.items.filter(is_active=True).select_related('product'):
            InvoiceItem.objects.create(
                invoice=invoice,
                product=cart_item.product,
                description=cart_item.product.name,
                sku=cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                discount_percent=float(cart.discount_percent) if cart.discount_percent > 0 else 0,
                tax_percent=9,
                warranty_description=cart_item.product.warranty or '',
                notes=cart_item.notes or '',
            )

        # محاسبه نهایی
        invoice.calculate_totals()

        # علامت‌گذاری Cart به عنوان سفارش داده شده
        from apps.basket.enums import CartStatus
        cart.status = CartStatus.ORDERED
        cart.save(update_fields=['status', 'updated_at'])

        logger.info(
            f"Invoice {invoice.invoice_number} created from Cart {cart.id} "
            f"for {user.get_display_name()}"
        )

        return invoice

    @classmethod
    @transaction.atomic
    def create_wallet_charge(cls, user, amount, payment_method='online_gateway',
                             description='', created_by=None):
        """
        ایجاد فاکتور شارژ کیف پول

        Args:
            user: کاربر
            amount: مبلغ شارژ
            payment_method: روش پرداخت
            description: توضیحات
            created_by: ایجاد کننده

        Returns:
            Invoice
        """
        invoice = Invoice.objects.create(
            user=user,
            invoice_type=InvoiceType.WALLET_CHARGE,
            status=InvoiceStatus.PENDING,
            payment_method=payment_method,
            total_amount=amount,
            paid_amount=0,
            remaining_amount=amount,
            notes=description,
            created_by=created_by,
        )

        # یک آیتم برای شارژ والت
        InvoiceItem.objects.create(
            invoice=invoice,
            description=description or _('Wallet Charge'),
            quantity=1,
            unit_price=amount,
            tax_percent=0,  # شارژ والت مالیات نداره
        )

        logger.info(
            f"Wallet charge invoice {invoice.invoice_number} created "
            f"for {user.get_display_name()}: {amount:,} Rials"
        )

        return invoice

    @classmethod
    @transaction.atomic
    def create_refund_invoice(cls, original_invoice, reason='', created_by=None):
        """
        ایجاد فاکتور برگشتی

        Args:
            original_invoice: فاکتور اصلی
            reason: دلیل برگشت
            created_by: ایجاد کننده

        Returns:
            Invoice
        """
        if original_invoice.status != InvoiceStatus.PAID:
            raise ValueError(_('Only paid invoices can be refunded.'))

        refund_invoice = Invoice.objects.create(
            user=original_invoice.user,
            invoice_type=InvoiceType.REFUND,
            status=InvoiceStatus.PENDING,
            related_invoice=original_invoice,
            total_amount=-original_invoice.total_amount,
            notes=f"Refund for {original_invoice.invoice_number}: {reason}",
            created_by=created_by,
        )

        # کپی آیتم‌ها با مقدار منفی
        for item in original_invoice.items.all():
            InvoiceItem.objects.create(
                invoice=refund_invoice,
                product=item.product,
                description=f"REFUND: {item.description}",
                sku=item.sku,
                quantity=item.quantity,
                unit_price=-item.unit_price,
                notes=reason,
            )

        refund_invoice.calculate_totals()

        # علامت‌گذاری فاکتور اصلی
        original_invoice.status = InvoiceStatus.REFUNDED
        original_invoice.save(update_fields=['status'])

        logger.info(
            f"Refund invoice {refund_invoice.invoice_number} created "
            f"for {original_invoice.invoice_number}"
        )

        return refund_invoice

    # ==================== Invoice Operations ====================

    @classmethod
    @transaction.atomic
    def convert_to_final(cls, invoice):
        """
        تبدیل پیش‌فاکتور به فاکتور نهایی

        Args:
            invoice: پیش‌فاکتور

        Returns:
            Invoice
        """
        if not invoice.is_proforma:
            raise ValueError(_('Only proforma can be converted.'))

        if invoice.status not in [InvoiceStatus.DRAFT, InvoiceStatus.PENDING]:
            raise ValueError(_('Invoice must be in draft or pending status.'))

        invoice.convert_to_final()
        invoice.status = InvoiceStatus.PENDING
        invoice.save()

        logger.info(f"Proforma {invoice.invoice_number} converted to final")

        return invoice

    @classmethod
    @transaction.atomic
    def update_invoice_status(cls, invoice, status, reason='', updated_by=None):
        """
        تغییر وضعیت فاکتور

        Args:
            invoice: فاکتور
            status: وضعیت جدید
            reason: دلیل
            updated_by: تغییر دهنده

        Returns:
            Invoice
        """
        old_status = invoice.status

        if status == InvoiceStatus.PAID:
            invoice.mark_as_paid()
        elif status == InvoiceStatus.CANCELLED:
            invoice.cancel(reason)
        else:
            invoice.status = status
            invoice.save()

        if updated_by:
            invoice.approved_by = updated_by
            invoice.approved_at = timezone.now()
            invoice.save()

        logger.info(
            f"Invoice {invoice.invoice_number} status changed: "
            f"{old_status} -> {status} by {updated_by.get_display_name() if updated_by else 'system'}"
        )

        return invoice

    @classmethod
    @transaction.atomic
    def record_payment(cls, invoice, amount, payment_method='card_to_card',
                       reference_code='', verified_by=None):
        """
        ثبت پرداخت برای فاکتور

        Args:
            invoice: فاکتور
            amount: مبلغ پرداختی
            payment_method: روش پرداخت
            reference_code: کد پیگیری
            verified_by: تایید کننده

        Returns:
            FinancialTransaction
        """
        amount = Decimal(str(amount))

        if not invoice.paid_amount:
            invoice.paid_amount = Decimal('0.00')

        if invoice.is_fully_paid:
            raise ValueError(_('Invoice is already fully paid.'))

        if amount <= 0:
            raise ValueError(_('Amount must be positive.'))

        if amount > invoice.balance:
            raise ValueError(
                _(f'Amount exceeds balance. Max: {invoice.balance:,}')
            )

        # ایجاد تراکنش
        transaction_obj = FinancialTransaction.objects.create(
            user=invoice.user,
            invoice=invoice,
            transaction_type=TransactionType.PAYMENT,
            amount=amount,
            status=PaymentStatus.VERIFIED if verified_by else PaymentStatus.PENDING,
            payment_method=payment_method,
            reference_code=reference_code,
            description=f"Payment for {invoice.invoice_number}",
            verified_by=verified_by,
            verified_at=timezone.now() if verified_by else None,
        )

        # آپدیت فاکتور
        invoice.add_payment(amount)

        logger.info(
            f"Payment recorded for {invoice.invoice_number}: "
            f"{amount:,} via {payment_method}"
        )

        return transaction_obj

    @classmethod
    @transaction.atomic
    def process_wallet_payment(cls, invoice, user):
        """
        پرداخت فاکتور با کیف پول

        Args:
            invoice: فاکتور
            user: کاربر (صاحب والت)

        Returns:
            FinancialTransaction
        """
        if not hasattr(user, 'wallet'):
            raise ValueError(_('User has no wallet.'))

        wallet = user.wallet
        amount = invoice.balance

        if wallet.available_balance < amount:
            raise ValueError(
                _(f'Insufficient wallet balance. Available: {wallet.available_balance:,}')
            )

        # برداشت از والت
        wallet.withdraw(amount)

        # ایجاد تراکنش
        transaction_obj = FinancialTransaction.objects.create(
            user=user,
            invoice=invoice,
            wallet=wallet,
            transaction_type=TransactionType.PAYMENT,
            amount=amount,
            status=PaymentStatus.VERIFIED,
            payment_method=PaymentMethod.WALLET,
            reference_code=f"WALLET-{invoice.invoice_number}",
            description=f"Wallet payment for {invoice.invoice_number}",
            verified_at=timezone.now(),
        )

        # آپدیت فاکتور
        invoice.mark_as_paid(PaymentMethod.WALLET)

        logger.info(
            f"Invoice {invoice.invoice_number} paid from wallet: {amount:,}"
        )

        return transaction_obj

    @classmethod
    @transaction.atomic
    def process_wallet_charge(cls, invoice, verified_by=None):
        """
        پردازش شارژ والت بعد از تایید پرداخت

        Args:
            invoice: فاکتور شارژ والت
            verified_by: تایید کننده

        Returns:
            FinancialTransaction
        """
        if not invoice.is_wallet_charge:
            raise ValueError(_('Not a wallet charge invoice.'))

        if not invoice.is_fully_paid:
            raise ValueError(_('Invoice is not fully paid.'))

        user = invoice.user

        # ایجاد یا دریافت والت
        from apps.accounts.models import Wallet
        wallet, created = Wallet.objects.get_or_create(user=user)

        # واریز به والت
        wallet.deposit(invoice.total_amount)

        # ایجاد تراکنش
        transaction_obj = FinancialTransaction.objects.create(
            user=user,
            invoice=invoice,
            wallet=wallet,
            transaction_type=TransactionType.WALLET_CHARGE,
            amount=invoice.total_amount,
            status=PaymentStatus.VERIFIED,
            payment_method=invoice.payment_method,
            reference_code=f"CHARGE-{invoice.invoice_number}",
            description=f"Wallet charged: {invoice.total_amount:,} Rials",
            verified_by=verified_by,
            verified_at=timezone.now(),
        )

        logger.info(
            f"Wallet charged for {user.get_display_name()}: "
            f"{invoice.total_amount:,} Rials"
        )

        return transaction_obj

    # ==================== Helpers ====================

    @staticmethod
    def _prepare_billing_info(billing_info):
        """آماده‌سازی اطلاعات صورتحساب"""
        if not billing_info:
            return {}

        return {
            'billing_name': billing_info.get('name', ''),
            'billing_company': billing_info.get('company', ''),
            'billing_national_id': billing_info.get('national_id', ''),
            'billing_economic_code': billing_info.get('economic_code', ''),
            'billing_address': billing_info.get('address', ''),
            'billing_postal_code': billing_info.get('postal_code', ''),
            'billing_phone': billing_info.get('phone', ''),
        }

    @classmethod
    def get_user_invoices(cls, user, invoice_type=None, status=None):
        """
        دریافت فاکتورهای کاربر

        Args:
            user: کاربر
            invoice_type: نوع فاکتور (اختیاری)
            status: وضعیت (اختیاری)

        Returns:
            QuerySet
        """
        queryset = Invoice.objects.filter(user=user)

        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')

    @classmethod
    def get_overdue_invoices(cls):
        """
        دریافت فاکتورهای معوق

        Returns:
            QuerySet
        """
        return Invoice.objects.filter(
            status__in=[InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID],
            payment_due_date__lt=timezone.now().date()
        ).order_by('payment_due_date')

    @classmethod
    @transaction.atomic
    def cancel_expired_invoices(cls):
        """
        لغو خودکار فاکتورهای منقضی شده

        Returns:
            int: تعداد فاکتورهای لغو شده
        """
        expired = Invoice.objects.filter(
            status__in=[InvoiceStatus.PENDING, InvoiceStatus.PARTIALLY_PAID],
            payment_due_date__lt=timezone.now().date() - timezone.timedelta(days=30)
        )

        count = expired.count()
        expired.update(status=InvoiceStatus.EXPIRED)

        logger.info(f"Cancelled {count} expired invoices")

        return count
