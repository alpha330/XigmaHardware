from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


@shared_task(name='website.send_contact_notification', max_retries=2)
def send_contact_notification(name, email, subject, message):
    """ارسال ایمیل تماس به ادمین"""
    try:
        from apps.accounts.models import User
        admin_emails = User.objects.filter(is_superuser=True, is_active=True, email__isnull=False).values_list('email', flat=True)

        if admin_emails:
            send_mail(
                subject=f'📩 Contact: {subject}',
                message=f'From: {name} ({email})\n\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails),
                fail_silently=False,
            )
        return f"Contact notification sent to {len(admin_emails)} admins"
    except Exception as e:
        logger.error(f"Contact notification failed: {str(e)}")