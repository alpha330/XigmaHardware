import logging
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.support.models import Ticket, TicketMessage
from apps.support.enums import TicketStatus

logger = logging.getLogger(__name__)


class TicketService:
    """
    سرویس مدیریت تیکت‌ها

    عملیات:
    - ایجاد تیکت
    - افزودن پیام
    - تغییر وضعیت
    - تخصیص
    - ارسال نوتیفیکیشن
    """

    @classmethod
    @db_transaction.atomic
    def create_ticket(cls, user, category, priority, subject, body,
                      order=None, product=None, ip_address=None):
        """
        ایجاد تیکت جدید

        Args:
            user: کاربر
            category: دسته‌بندی
            priority: اولویت
            subject: موضوع
            body: متن
            order: سفارش مرتبط (اختیاری)
            product: محصول مرتبط (اختیاری)
            ip_address: IP کاربر

        Returns:
            Ticket
        """
        ticket = Ticket.objects.create(
            user=user,
            category=category,
            priority=priority,
            subject=subject,
            body=body,
            order=order,
            product=product,
            status=TicketStatus.OPEN,
            ip_address=ip_address,
        )

        logger.info(
            f"Ticket created: {ticket.ticket_number} by "
            f"{user.email or user.mobile} [{category}]"
        )

        # ارسال ایمیل به کاربر
        from apps.support.tasks import send_ticket_created_email
        send_ticket_created_email.delay(str(ticket.id))

        # ارسال نوتیفیکیشن به ادمین
        from apps.support.tasks import send_ticket_admin_notification
        send_ticket_admin_notification.delay(str(ticket.id), 'new_ticket')

        return ticket

    @classmethod
    @db_transaction.atomic
    def add_message(cls, ticket, sender, body, is_staff=False,
                    is_internal=False, attachment=None, ip=None):
        """
        افزودن پیام به تیکت

        Args:
            ticket: تیکت
            sender: فرستنده
            body: متن
            is_staff: پاسخ پشتیبانی؟
            is_internal: یادداشت داخلی؟
            attachment: فایل پیوست
            ip: IP

        Returns:
            TicketMessage
        """
        msg = ticket.add_message(
            sender=sender,
            body=body,
            is_staff=is_staff,
            is_internal=is_internal,
            attachment=attachment,
            ip=ip,
        )

        # ارسال نوتیفیکیشن
        from apps.support.tasks import send_ticket_reply_email

        if is_staff and not is_internal:
            # ایمیل به کاربر
            send_ticket_reply_email.delay(str(ticket.id), str(msg.id))
        elif not is_staff:
            # نوتیفیکیشن به ادمین
            from apps.support.tasks import send_ticket_admin_notification
            send_ticket_admin_notification.delay(str(ticket.id), 'new_reply')

        logger.info(f"Message added to {ticket.ticket_number} by {sender.get_display_name()}")

        return msg

    @classmethod
    @db_transaction.atomic
    def update_status(cls, ticket, status, updated_by=None):
        """
        تغییر وضعیت تیکت

        Args:
            ticket: تیکت
            status: وضعیت جدید
            updated_by: تغییر دهنده

        Returns:
            Ticket
        """
        old_status = ticket.status
        ticket.status = status

        if status == TicketStatus.RESOLVED:
            ticket.resolved_at = timezone.now()
        elif status == TicketStatus.CLOSED:
            ticket.closed_at = timezone.now()

        ticket.save()

        # ارسال نوتیفیکیشن
        from apps.support.tasks import send_ticket_status_email
        send_ticket_status_email.delay(str(ticket.id), status, old_status)

        logger.info(
            f"Ticket {ticket.ticket_number} status: {old_status} -> {status} "
            f"by {updated_by.get_display_name() if updated_by else 'system'}"
        )

        return ticket

    @classmethod
    @db_transaction.atomic
    def assign_ticket(cls, ticket, staff_user):
        """
        تخصیص تیکت به پشتیبان

        Args:
            ticket: تیکت
            staff_user: کاربر پشتیبان

        Returns:
            Ticket
        """
        ticket.assign_to(staff_user)

        logger.info(f"Ticket {ticket.ticket_number} assigned to {staff_user.get_display_name()}")

        return ticket

    @classmethod
    def get_user_tickets(cls, user, status=None):
        """تیکت‌های یک کاربر"""
        qs = Ticket.objects.filter(user=user)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    @classmethod
    def get_open_tickets(cls):
        """تیکت‌های باز"""
        return Ticket.objects.filter(status__in=[TicketStatus.OPEN, TicketStatus.IN_PROGRESS])

    @classmethod
    def get_unassigned_tickets(cls):
        """تیکت‌های تخصیص نیافته"""
        return Ticket.objects.filter(assigned_to__isnull=True, status=TicketStatus.OPEN)

    @classmethod
    def get_overdue_tickets(cls):
        """تیکت‌های overdue"""
        return [t for t in cls.get_open_tickets() if t.is_overdue]