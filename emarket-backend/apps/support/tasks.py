"""
Celery Tasks برای Support

شامل:
- ایمیل ایجاد تیکت
- ایمیل پاسخ تیکت
- ایمیل تغییر وضعیت
- نوتیفیکیشن ادمین
- یادآوری گارانتی
"""

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task(name='support.send_ticket_created_email', bind=True, max_retries=3)
def send_ticket_created_email(self, ticket_id):
    """
    ایمیل تأیید ایجاد تیکت به کاربر

    Args:
        ticket_id: شناسه تیکت
    """
    from apps.support.models import Ticket

    try:
        ticket = Ticket.objects.select_related('user').get(id=ticket_id)

        if not ticket.user.email:
            return

        try:
            import jdatetime
            date_str = jdatetime.datetime.fromgregorian(datetime=ticket.created_at).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            date_str = ticket.created_at.strftime('%Y-%m-%d %H:%M')

        context = {
            'user_name': ticket.user.get_display_name(),
            'ticket_number': ticket.ticket_number,
            'subject': ticket.subject,
            'category': ticket.get_category_display(),
            'priority': ticket.get_priority_display(),
            'date': date_str,
            'body': ticket.body[:200],
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
            'ticket_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/support/tickets/{ticket.id}/",
        }

        html = render_to_string('support/emails/ticket_created.html', context)
        text = render_to_string('support/emails/ticket_created.txt', context)

        email = EmailMultiAlternatives(
            subject=f'🎫 تیکت {ticket.ticket_number} ثبت شد - XigmaHardware',
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[ticket.user.email],
        )
        email.attach_alternative(html, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Ticket created email sent: {ticket.ticket_number}")
        return f"Sent: {ticket.ticket_number}"

    except Exception as e:
        logger.error(f"Ticket email failed: {str(e)}")
        raise self.retry(exc=e)


@shared_task(name='support.send_ticket_reply_email', bind=True, max_retries=3)
def send_ticket_reply_email(self, ticket_id, message_id):
    """
    ایمیل پاسخ تیکت به کاربر

    Args:
        ticket_id: شناسه تیکت
        message_id: شناسه پیام
    """
    from apps.support.models import Ticket, TicketMessage

    try:
        ticket = Ticket.objects.select_related('user').get(id=ticket_id)
        message = TicketMessage.objects.select_related('sender').get(id=message_id)

        if not ticket.user.email:
            return

        try:
            import jdatetime
            date_str = jdatetime.datetime.fromgregorian(datetime=message.created_at).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            date_str = message.created_at.strftime('%Y-%m-%d %H:%M')

        context = {
            'user_name': ticket.user.get_display_name(),
            'ticket_number': ticket.ticket_number,
            'subject': ticket.subject,
            'reply_body': message.body[:300],
            'replier_name': message.sender.get_display_name(),
            'date': date_str,
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
            'ticket_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/support/tickets/{ticket.id}/",
        }

        html = render_to_string('support/emails/ticket_reply.html', context)
        text = render_to_string('support/emails/ticket_reply.txt', context)

        email = EmailMultiAlternatives(
            subject=f'📩 پاسخ تیکت {ticket.ticket_number} - XigmaHardware',
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[ticket.user.email],
        )
        email.attach_alternative(html, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Ticket reply email sent: {ticket.ticket_number}")
        return f"Sent reply: {ticket.ticket_number}"

    except Exception as e:
        logger.error(f"Reply email failed: {str(e)}")
        raise self.retry(exc=e)


@shared_task(name='support.send_ticket_status_email', bind=True, max_retries=3)
def send_ticket_status_email(self, ticket_id, new_status, old_status):
    """
    ایمیل تغییر وضعیت تیکت

    Args:
        ticket_id: شناسه تیکت
        new_status: وضعیت جدید
        old_status: وضعیت قبلی
    """
    from apps.support.models import Ticket

    try:
        ticket = Ticket.objects.select_related('user').get(id=ticket_id)

        if not ticket.user.email:
            return

        context = {
            'user_name': ticket.user.get_display_name(),
            'ticket_number': ticket.ticket_number,
            'subject': ticket.subject,
            'old_status': old_status,
            'new_status': new_status,
            'new_status_display': dict(Ticket._meta.get_field('status').choices).get(new_status, new_status),
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
            'ticket_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/support/tickets/{ticket.id}/",
        }

        html = render_to_string('support/emails/ticket_status.html', context)
        text = render_to_string('support/emails/ticket_status.txt', context)

        email = EmailMultiAlternatives(
            subject=f'🔄 وضعیت تیکت {ticket.ticket_number} بروزرسانی شد',
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[ticket.user.email],
        )
        email.attach_alternative(html, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Status email sent: {ticket.ticket_number} {old_status}->{new_status}")
        return f"Status sent: {ticket.ticket_number}"

    except Exception as e:
        logger.error(f"Status email failed: {str(e)}")
        raise self.retry(exc=e)


@shared_task(name='support.send_ticket_admin_notification', bind=True, max_retries=2)
def send_ticket_admin_notification(self, ticket_id, event_type):
    """
    نوتیفیکیشن ادمین برای تیکت جدید/پاسخ

    Args:
        ticket_id: شناسه تیکت
        event_type: new_ticket / new_reply
    """
    from apps.support.models import Ticket
    from apps.accounts.models import User

    try:
        ticket = Ticket.objects.select_related('user').get(id=ticket_id)

        admin_emails = User.objects.filter(
            is_superuser=True, is_active=True, email__isnull=False
        ).exclude(email='').values_list('email', flat=True)

        if not admin_emails:
            return "No admin emails"

        if event_type == 'new_ticket':
            subject = f'🎫 تیکت جدید: {ticket.ticket_number} - {ticket.get_priority_display()}'
            body = f"""
            تیکت جدید ثبت شد:
            شماره: {ticket.ticket_number}
            کاربر: {ticket.user.get_display_name()}
            موضوع: {ticket.subject}
            اولویت: {ticket.get_priority_display()}
            دسته: {ticket.get_category_display()}
            """
        else:
            subject = f'📩 پاسخ جدید: {ticket.ticket_number}'
            body = f"""
            پاسخ جدید در تیکت {ticket.ticket_number}:
            کاربر: {ticket.user.get_display_name()}
            موضوع: {ticket.subject}
            """

        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(admin_emails),
        )
        email.send(fail_silently=False)

        return f"Admin notified: {len(admin_emails)} recipients"

    except Exception as e:
        logger.error(f"Admin notification failed: {str(e)}")


@shared_task(name='support.send_warranty_expiry_reminder')
def send_warranty_expiry_reminder():
    """
    یادآوری گارانتی‌های در شرف انقضا

    اجرا: هر روز ساعت ۱۰ صبح
    """
    from apps.support.services.warranty_service import WarrantyService

    expiring = WarrantyService.get_expiring_soon(days=30)

    count = 0
    for warranty in expiring:
        if warranty.user.email:
            try:
                context = {
                    'user_name': warranty.user.get_display_name(),
                    'product_name': warranty.product.name,
                    'warranty_number': warranty.warranty_number,
                    'end_date': warranty.end_date,
                    'days_remaining': warranty.days_remaining,
                }

                html = render_to_string('support/emails/warranty_expiring.html', context)
                text = render_to_string('support/emails/warranty_expiring.txt', context)

                email = EmailMultiAlternatives(
                    subject=f'⏰ گارانتی {warranty.product.name} در حال اتمام است',
                    body=text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[warranty.user.email],
                )
                email.attach_alternative(html, "text/html")
                email.send(fail_silently=False)
                count += 1
            except Exception as e:
                logger.error(f"Warranty reminder failed: {str(e)}")

    return f"Warranty reminders sent: {count}"