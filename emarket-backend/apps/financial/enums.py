from django.db import models
from django.utils.translation import gettext_lazy as _


class InvoiceType(models.TextChoices):
    """نوع فاکتور"""
    PROFORMA = 'proforma', _('Proforma Invoice')      # پیش‌فاکتور
    FINAL = 'final', _('Final Invoice')                # فاکتور نهایی
    WALLET_CHARGE = 'wallet_charge', _('Wallet Charge') # شارژ کیف پول
    REFUND = 'refund', _('Refund Invoice')             # فاکتور برگشتی


class InvoiceStatus(models.TextChoices):
    """وضعیت فاکتور"""
    DRAFT = 'draft', _('Draft')
    PENDING = 'pending', _('Pending Payment')
    PAID = 'paid', _('Paid')
    PARTIALLY_PAID = 'partially_paid', _('Partially Paid')
    CANCELLED = 'cancelled', _('Cancelled')
    EXPIRED = 'expired', _('Expired')
    REFUNDED = 'refunded', _('Refunded')


class PaymentMethod(models.TextChoices):
    """روش پرداخت"""
    WALLET = 'wallet', _('Wallet')
    CARD_TO_CARD = 'card_to_card', _('Card to Card')
    BANK_TRANSFER = 'bank_transfer', _('Bank Transfer')
    ONLINE_GATEWAY = 'online_gateway', _('Online Gateway')
    CHEQUE = 'cheque', _('Cheque')
    CASH = 'cash', _('Cash')


class PaymentStatus(models.TextChoices):
    """وضعیت پرداخت"""
    PENDING = 'pending', _('Pending')
    VERIFIED = 'verified', _('Verified')
    FAILED = 'failed', _('Failed')
    REFUNDED = 'refunded', _('Refunded')


class TransactionType(models.TextChoices):
    """نوع تراکنش مالی"""
    PAYMENT = 'payment', _('Payment')
    DEPOSIT = 'deposit', _('Deposit')
    WITHDRAW = 'withdraw', _('Withdraw')
    REFUND = 'refund', _('Refund')
    COMMISSION = 'commission', _('Commission')
    ADJUSTMENT = 'adjustment', _('Adjustment')
    WALLET_CHARGE = 'wallet_charge', _('Wallet Charge')


class ReportType(models.TextChoices):
    """نوع گزارش"""
    DAILY = 'daily', _('Daily')
    WEEKLY = 'weekly', _('Weekly')
    MONTHLY = 'monthly', _('Monthly')
    QUARTERLY = 'quarterly', _('Quarterly')
    YEARLY = 'yearly', _('Yearly')
    CUSTOM = 'custom', _('Custom Range')


class ReportFormat(models.TextChoices):
    """فرمت خروجی گزارش"""
    JSON = 'json', _('JSON')
    CSV = 'csv', _('CSV')
    EXCEL = 'excel', _('Excel')
    PDF = 'pdf', _('PDF')