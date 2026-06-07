import logging
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.support.models import Warranty
from apps.support.enums import WarrantyStatus

logger = logging.getLogger(__name__)


class WarrantyService:
    """
    سرویس مدیریت گارانتی

    عملیات:
    - ثبت گارانتی خودکار بعد از خرید
    - استعلام گارانتی
    - ثبت ادعا
    - بررسی وضعیت
    """

    @classmethod
    @db_transaction.atomic
    def create_warranty(cls, user, product, invoice, duration_months=12,
                        serial_number='', warranty_type='Manufacturer'):
        """
        ایجاد گارانتی جدید (بعد از خرید موفق)

        Args:
            user: کاربر
            product: محصول
            invoice: فاکتور
            duration_months: مدت گارانتی (ماه)
            serial_number: شماره سریال
            warranty_type: نوع گارانتی

        Returns:
            Warranty
        """
        from datetime import timedelta

        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=duration_months * 30)

        warranty = Warranty.objects.create(
            user=user,
            product=product,
            invoice=invoice,
            start_date=start_date,
            end_date=end_date,
            duration_months=duration_months,
            serial_number=serial_number,
            warranty_type=warranty_type,
            status=WarrantyStatus.ACTIVE,
        )

        logger.info(
            f"Warranty created: {warranty.warranty_number} for "
            f"{user.email or user.mobile} - {product.name}"
        )

        return warranty

    @classmethod
    @db_transaction.atomic
    def claim_warranty(cls, warranty, description):
        """
        ثبت ادعای گارانتی

        Args:
            warranty: گارانتی
            description: شرح مشکل

        Returns:
            Warranty
        """
        if not warranty.is_active:
            raise ValueError(_('Warranty is not active.'))

        warranty.status = WarrantyStatus.CLAIMED
        warranty.claim_date = timezone.now().date()
        warranty.claim_description = description
        warranty.save()

        logger.info(f"Warranty claim: {warranty.warranty_number}")

        return warranty

    @classmethod
    @db_transaction.atomic
    def resolve_warranty(cls, warranty, resolution, status=WarrantyStatus.COMPLETED):
        """
        حل و فصل ادعای گارانتی

        Args:
            warranty: گارانتی
            resolution: شرح راه‌حل
            status: وضعیت نهایی

        Returns:
            Warranty
        """
        warranty.status = status
        warranty.resolution = resolution
        warranty.save()

        logger.info(f"Warranty resolved: {warranty.warranty_number} -> {status}")

        return warranty

    @classmethod
    def check_by_serial(cls, serial_number):
        """
        استعلام گارانتی با شماره سریال

        Args:
            serial_number: شماره سریال

        Returns:
            Warranty or None
        """
        return Warranty.objects.filter(serial_number=serial_number).first()

    @classmethod
    def get_user_warranties(cls, user):
        """گارانتی‌های کاربر"""
        return Warranty.objects.filter(user=user).order_by('-created_at')

    @classmethod
    def get_expiring_soon(cls, days=30):
        """گارانتی‌های در شرف انقضا"""
        from datetime import timedelta
        deadline = timezone.now().date() + timedelta(days=days)
        return Warranty.objects.filter(
            status=WarrantyStatus.ACTIVE,
            end_date__lte=deadline,
            end_date__gte=timezone.now().date(),
        )