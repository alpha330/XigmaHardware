"""
Celery Tasks برای Logistics

شامل:
- نوتیفیکیشن تغییر وضعیت ارسال
- ایمیل به خریدار
- ایمیل به ادمین
- (آینده: SMS)
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
    name='logistics.send_shipment_status_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_shipment_status_email(self, shipment_id, status, extra_info=None):
    """
    ارسال ایمیل تغییر وضعیت ارسال

    Args:
        shipment_id: شناسه محموله
        status: وضعیت جدید
        extra_info: اطلاعات اضافی
    """
    from apps.logistics.models import Shipment

    try:
        shipment = Shipment.objects.select_related(
            'user', 'courier', 'destination_address',
            'origin_warehouse',
        ).get(id=shipment_id)

        if not shipment.user or not shipment.user.email:
            logger.warning(f"No email for shipment {shipment_id}")
            return

        # انتخاب قالب ایمیل بر اساس وضعیت
        template_map = {
            'assigned': 'logistics/emails/courier_assigned.html',
            'picked_up': 'logistics/emails/picked_up.html',
            'in_transit': 'logistics/emails/in_transit.html',
            'delivered': 'logistics/emails/delivered.html',
            'cancelled': 'logistics/emails/cancelled.html',
        }

        subject_map = {
            'assigned': _('🚀 Courier Assigned - Order #{}'),
            'picked_up': _('📦 Package Picked Up - Order #{}'),
            'in_transit': _('🛵 Package In Transit - Order #{}'),
            'delivered': _('✅ Package Delivered - Order #{}'),
            'cancelled': _('❌ Shipment Cancelled - Order #{}'),
        }

        template_name = template_map.get(status, 'logistics/emails/status_update.html')
        subject = subject_map.get(status, _('📦 Shipment Update - Order #{}')).format(
            str(shipment.id)[:8]
        )

        # آماده‌سازی context
        try:
            import jdatetime
            now_jalali = jdatetime.datetime.fromgregorian(datetime=timezone.now())
            date_str = now_jalali.strftime('%Y/%m/%d %H:%M')
        except ImportError:
            date_str = timezone.now().strftime('%Y-%m-%d %H:%M')

        context = {
            'user_name': shipment.user.get_display_name(),
            'shipment_id': str(shipment.id)[:8],
            'status': status,
            'status_display': shipment.get_status_display(),
            'date': date_str,
            'courier_name': shipment.courier.name if shipment.courier else '-',
            'courier_phone': shipment.courier.phone if shipment.courier else '-',
            'tracking_code': shipment.courier_tracking_code or str(shipment.id)[:8],
            'origin': shipment.origin_warehouse.name if shipment.origin_warehouse else 'XigmaHardware Warehouse',
            'destination': shipment.destination_address.full_address if shipment.destination_address else '-',
            'recipient_name': shipment.destination_address.recipient_name if shipment.destination_address else shipment.user.get_display_name(),
            'estimated_delivery': extra_info.get('estimated_delivery', '') if extra_info else '',
            'distance_km': float(shipment.distance_km) if shipment.distance_km else 0,
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@xigmahardware.com'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'tracking_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/shipments/{shipment.id}/tracking/",
        }

        # رندر قالب‌ها
        html_content = render_to_string(template_name, context)
        text_content = render_to_string(template_name.replace('.html', '.txt'), context)

        # ارسال به خریدار
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[shipment.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Shipment email sent to {shipment.user.email}: {status}")

        # ارسال به ادمین (برای وضعیت‌های مهم)
        if status in ['delivered', 'cancelled', 'assigned']:
            send_admin_notification.delay(shipment_id, status, html_content, text_content)

        return f"Shipment email sent: {shipment_id} - {status}"

    except Shipment.DoesNotExist:
        logger.error(f"Shipment {shipment_id} not found")
        return f"Shipment {shipment_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send shipment email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='logistics.send_admin_notification',
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def send_admin_notification(self, shipment_id, status, html_content, text_content):
    """
    ارسال نوتیفیکیشن به ادمین

    Args:
        shipment_id: شناسه محموله
        status: وضعیت
        html_content: محتوای HTML
        text_content: محتوای متنی
    """
    from apps.accounts.models import User

    admin_emails = User.objects.filter(
        is_superuser=True,
        is_active=True,
        email__isnull=False,
    ).exclude(email='').values_list('email', flat=True)

    # همچنین به stock_keeper ها
    stock_keepers = User.objects.filter(
        role='stock_keeper',
        is_active=True,
        email__isnull=False,
    ).exclude(email='').values_list('email', flat=True)

    all_emails = list(set(list(admin_emails) + list(stock_keepers)))

    if all_emails:
        subject = f'📦 [ADMIN] Shipment #{str(shipment_id)[:8]} - {status.upper()}'

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=all_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Admin notification sent to {len(all_emails)} recipients")
        return f"Admin notification sent: {len(all_emails)} recipients"

    return "No admin emails found"


@shared_task(
    name='logistics.send_shipment_created_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_shipment_created_email(self, shipment_id):
    """
    ارسال ایمیل ایجاد محموله جدید

    Args:
        shipment_id: شناسه محموله
    """
    from apps.logistics.models import Shipment

    try:
        shipment = Shipment.objects.select_related(
            'user', 'destination_address', 'origin_warehouse',
        ).get(id=shipment_id)

        if not shipment.user or not shipment.user.email:
            return

        try:
            import jdatetime
            now = jdatetime.datetime.fromgregorian(datetime=timezone.now())
            date_str = now.strftime('%Y/%m/%d %H:%M')
            delivery_date = now + timezone.timedelta(hours=2)
            estimated = delivery_date.strftime('%Y/%m/%d %H:%M')
        except ImportError:
            date_str = timezone.now().strftime('%Y-%m-%d %H:%M')
            estimated = (timezone.now() + timezone.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')

        context = {
            'user_name': shipment.user.get_display_name(),
            'shipment_id': str(shipment.id)[:8],
            'date': date_str,
            'origin': shipment.origin_warehouse.name if shipment.origin_warehouse else 'XigmaHardware',
            'destination': shipment.destination_address.full_address if shipment.destination_address else '-',
            'recipient_name': shipment.destination_address.recipient_name if shipment.destination_address else shipment.user.get_display_name(),
            'tracking_code': str(shipment.id)[:8],
            'estimated_delivery': estimated,
            'items_count': shipment.invoice.items_count if shipment.invoice else 0,
            'site_name': getattr(settings, 'SITE_NAME', 'XigmaHardware'),
            'tracking_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/shipments/{shipment.id}/tracking/",
        }

        html_content = render_to_string('logistics/emails/shipment_created.html', context)
        text_content = render_to_string('logistics/emails/shipment_created.txt', context)

        subject = _('📦 Shipment Created - Order #{}').format(str(shipment.id)[:8])

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[shipment.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info(f"Shipment created email sent to {shipment.user.email}")

        return f"Created email sent: {shipment_id}"

    except Shipment.DoesNotExist:
        return f"Shipment {shipment_id} not found"
    except Exception as exc:
        logger.error(f"Failed to send created email: {str(exc)}")
        raise self.retry(exc=exc)