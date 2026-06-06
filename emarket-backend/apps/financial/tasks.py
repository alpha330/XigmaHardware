"""
Celery Tasks for Financial App

شامل تسک‌های:
- ارسال ایمیل پیش‌فاکتور
- ارسال ایمیل فاکتور نهایی
- ارسال ایمیل پرداخت
- ارسال ایمیل شارژ والت
- لغو خودکار فاکتورهای منقضی
"""

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task(
    name='financial.send_proforma_invoice_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_proforma_invoice_email(self, invoice_id):
    """
    ارسال ایمیل پیش‌فاکتور به مشتری و ادمین

    Args:
        invoice_id: شناسه فاکتور
    """
    from apps.financial.models import Invoice

    try:
        invoice = Invoice.objects.select_related('user').prefetch_related('items').get(id=invoice_id)

        if not invoice.user or not invoice.user.email:
            logger.warning(f"No email for invoice {invoice.invoice_number}")
            return

        # تاریخ شمسی
        try:
            import jdatetime
            created_date = jdatetime.datetime.fromgregorian(
                datetime=invoice.created_at
            ).strftime('%Y/%m/%d %H:%M')
            payment_due = jdatetime.date.fromgregorian(
                date=invoice.payment_due_date
            ).strftime('%Y/%m/%d') if invoice.payment_due_date else '-'
        except ImportError:
            created_date = invoice.created_at.strftime('%Y-%m-%d %H:%M')
            payment_due = invoice.payment_due_date.strftime('%Y-%m-%d') if invoice.payment_due_date else '-'

        # آماده‌سازی اقلام
        items = []
        for item in invoice.items.all():
            items.append({
                'description': item.description[:100],
                'quantity': item.quantity,
                'total_price': f'{int(item.total_price):,}',
            })

        context = {
            'user_name': invoice.user.get_display_name(),
            'invoice_number': invoice.invoice_number,
            'created_date': created_date,
            'total_amount': f'{int(invoice.total_amount):,}',
            'payment_due_date': payment_due,
            'items': items,
            'invoice_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/invoices/{invoice.id}/",
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
        }

        # رندر قالب‌ها
        html_content = render_to_string('financial/emails/proforma_created.html', context)
        text_content = render_to_string('financial/emails/proforma_created.txt', context)

        subject = f'📄 پیش‌فاکتور {invoice.invoice_number} - XigmaHardware'

        # ارسال به مشتری
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Proforma email sent to {invoice.user.email}: {invoice.invoice_number}")

        # ارسال به ادمین‌ها
        send_to_admins.delay(
            subject=f'📄 پیش‌فاکتور جدید: {invoice.invoice_number}',
            html_content=html_content,
            text_content=text_content,
        )

        return f"Proforma email sent: {invoice.invoice_number}"

    except Invoice.DoesNotExist:
        logger.error(f"Invoice {invoice_id} not found")
        return f"Invoice {invoice_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send proforma email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='financial.send_final_invoice_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_final_invoice_email(self, invoice_id):
    """
    ارسال ایمیل فاکتور نهایی به مشتری و ادمین

    Args:
        invoice_id: شناسه فاکتور
    """
    from apps.financial.models import Invoice

    try:
        invoice = Invoice.objects.select_related('user').get(id=invoice_id)

        if not invoice.user or not invoice.user.email:
            logger.warning(f"No email for invoice {invoice.invoice_number}")
            return

        try:
            import jdatetime
            created_date = jdatetime.datetime.fromgregorian(
                datetime=invoice.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            created_date = invoice.created_at.strftime('%Y-%m-%d %H:%M')

        context = {
            'user_name': invoice.user.get_display_name(),
            'invoice_number': invoice.invoice_number,
            'created_date': created_date,
            'total_amount': f'{int(invoice.total_amount):,}',
            'paid_amount': f'{int(invoice.paid_amount):,}',
            'remaining_amount': f'{int(invoice.remaining_amount):,}',
            'payment_method': invoice.get_payment_method_display() if invoice.payment_method else '',
            'is_paid': invoice.is_fully_paid,
            'invoice_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/invoices/{invoice.id}/",
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
        }

        html_content = render_to_string('financial/emails/invoice_final.html', context)
        text_content = render_to_string('financial/emails/invoice_final.txt', context)

        subject = f'✅ فاکتور نهایی {invoice.invoice_number} - XigmaHardware'

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Final invoice email sent to {invoice.user.email}: {invoice.invoice_number}")

        # ارسال به ادمین‌ها
        send_to_admins.delay(
            subject=f'✅ فاکتور نهایی: {invoice.invoice_number}',
            html_content=html_content,
            text_content=text_content,
        )

        return f"Final invoice email sent: {invoice.invoice_number}"

    except Invoice.DoesNotExist:
        return f"Invoice {invoice_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send final invoice email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='financial.send_payment_received_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_payment_received_email(self, transaction_id):
    """
    ارسال ایمیل تایید پرداخت

    Args:
        transaction_id: شناسه تراکنش
    """
    from apps.financial.models import FinancialTransaction

    try:
        transaction = FinancialTransaction.objects.select_related(
            'user', 'invoice'
        ).get(id=transaction_id)

        if not transaction.user or not transaction.user.email:
            return

        try:
            import jdatetime
            paid_date = jdatetime.datetime.fromgregorian(
                datetime=transaction.transaction_date
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            paid_date = transaction.transaction_date.strftime('%Y-%m-%d %H:%M')

        context = {
            'user_name': transaction.user.get_display_name(),
            'invoice_number': transaction.invoice.invoice_number if transaction.invoice else '-',
            'paid_amount': f'{int(transaction.amount):,}',
            'payment_method': transaction.get_payment_method_display(),
            'reference_code': transaction.reference_code or '-',
            'paid_date': paid_date,
            'is_fully_paid': transaction.invoice.is_fully_paid if transaction.invoice else False,
            'remaining_amount': f'{int(transaction.invoice.remaining_amount):,}' if transaction.invoice else '0',
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
        }

        html_content = render_to_string('financial/emails/payment_received.html', context)
        text_content = render_to_string('financial/emails/payment_received.txt', context)

        subject = f'💳 پرداخت دریافت شد - {context["invoice_number"]}'

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[transaction.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Payment received email sent to {transaction.user.email}")

        return f"Payment email sent: {transaction.transaction_number}"

    except FinancialTransaction.DoesNotExist:
        return f"Transaction {transaction_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send payment email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='financial.send_wallet_charged_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_wallet_charged_email(self, transaction_id):
    """
    ارسال ایمیل شارژ کیف پول

    Args:
        transaction_id: شناسه تراکنش
    """
    from apps.financial.models import FinancialTransaction

    try:
        transaction = FinancialTransaction.objects.select_related(
            'user', 'wallet'
        ).get(id=transaction_id)

        if not transaction.user or not transaction.user.email:
            return

        try:
            import jdatetime
            charge_date = jdatetime.datetime.fromgregorian(
                datetime=transaction.transaction_date
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            charge_date = transaction.transaction_date.strftime('%Y-%m-%d %H:%M')

        wallet_balance = transaction.wallet.balance if transaction.wallet else 0

        context = {
            'user_name': transaction.user.get_display_name(),
            'amount': f'{int(transaction.amount):,}',
            'payment_method': transaction.get_payment_method_display(),
            'transaction_number': transaction.transaction_number,
            'charge_date': charge_date,
            'wallet_balance': f'{int(wallet_balance):,}',
            'wallet_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/wallet/",
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
        }

        html_content = render_to_string('financial/emails/wallet_charged.html', context)
        text_content = render_to_string('financial/emails/wallet_charged.txt', context)

        subject = f'💰 کیف پول شارژ شد - {context["amount"]} ریال'

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[transaction.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Wallet charged email sent to {transaction.user.email}")

        return f"Wallet charged email sent: {transaction.transaction_number}"

    except FinancialTransaction.DoesNotExist:
        return f"Transaction {transaction_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send wallet charged email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='financial.send_to_admins',
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def send_to_admins(self, subject, html_content, text_content):
    """
    ارسال ایمیل به همه ادمین‌ها

    Args:
        subject: موضوع
        html_content: محتوای HTML
        text_content: محتوای متنی
    """
    from apps.accounts.models import User

    admin_emails = User.objects.filter(
        is_superuser=True,
        is_active=True,
        email__isnull=False,
    ).exclude(email='').values_list('email', flat=True)

    if admin_emails:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(admin_emails),
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Admin notification sent to {len(admin_emails)} admins")
        return f"Sent to {len(admin_emails)} admins"

    return "No admin emails found"


@shared_task(
    name='financial.cancel_expired_invoices',
)
def cancel_expired_invoices():
    """
    لغو خودکار فاکتورهای منقضی شده

    اجرا: هر روز ساعت ۱ صبح
    """
    from apps.financial.services.invoice_service import InvoiceService

    count = InvoiceService.cancel_expired_invoices()
    logger.info(f"Auto-cancelled {count} expired invoices")
    return f"Cancelled {count} invoices"