"""
سرویس مدیریت آدرس‌ها
"""

import logging
from django.db import transaction as db_transaction
from django.utils.translation import gettext_lazy as _
from apps.logistics.models import UserAddress

logger = logging.getLogger(__name__)


class AddressService:
    """
    سرویس مدیریت آدرس‌های کاربران

    عملیات:
    - ایجاد آدرس
    - بروزرسانی
    - تنظیم پیش‌فرض
    - اعتبارسنجی GPS
    - Geocoding (آینده)
    """

    @classmethod
    @db_transaction.atomic
    def create_address(cls, user, data: dict) -> UserAddress:
        """
        ایجاد آدرس جدید

        Args:
            user: کاربر
            data: داده‌های آدرس

        Returns:
            UserAddress
        """
        # اگر اولین آدرس هست، پیش‌فرض بشه
        is_first = not UserAddress.objects.filter(user=user).exists()

        if is_first or data.get('is_default'):
            # غیرفعال کردن پیش‌فرض قبلی
            if not is_first:
                UserAddress.objects.filter(user=user, is_default=True).update(is_default=False)
            data['is_default'] = True

        address = UserAddress.objects.create(user=user, **data)

        logger.info(f"Address created for user {user.email or user.mobile}: {address.title}")

        return address

    @classmethod
    @db_transaction.atomic
    def update_address(cls, address: UserAddress, data: dict) -> UserAddress:
        """
        بروزرسانی آدرس

        Args:
            address: آدرس
            data: داده‌های جدید

        Returns:
            UserAddress
        """
        allowed = [
            'address_type', 'title', 'recipient_name', 'recipient_mobile',
            'country', 'province', 'city', 'district', 'postal_code',
            'address_line', 'plaque', 'unit', 'floor',
            'latitude', 'longitude',
            'google_place_id', 'google_formatted_address',
            'delivery_instructions', 'is_active',
        ]

        for field in allowed:
            if field in data:
                setattr(address, field, data[field])

        address.save()

        logger.info(f"Address updated: {address.id}")

        return address

    @classmethod
    @db_transaction.atomic
    def set_as_default(cls, address: UserAddress) -> UserAddress:
        """
        تنظیم به عنوان آدرس پیش‌فرض

        Args:
            address: آدرس

        Returns:
            UserAddress
        """
        address.set_as_default()

        logger.info(f"Address {address.id} set as default")

        return address

    @classmethod
    @db_transaction.atomic
    def delete_address(cls, address: UserAddress) -> None:
        """
        حذف نرم آدرس

        Args:
            address: آدرس
        """
        was_default = address.is_default
        address.is_active = False
        address.is_default = False
        address.save()

        # اگر پیش‌فرض بود، یه آدرس دیگه رو پیش‌فرض کن
        if was_default:
            next_address = UserAddress.objects.filter(
                user=address.user,
                is_active=True,
            ).first()

            if next_address:
                next_address.set_as_default()

        logger.info(f"Address deleted: {address.id}")

    @classmethod
    def get_default_address(cls, user) -> UserAddress:
        """
        دریافت آدرس پیش‌فرض کاربر

        Args:
            user: کاربر

        Returns:
            UserAddress or None
        """
        return UserAddress.objects.filter(
            user=user,
            is_default=True,
            is_active=True,
        ).first()

    @classmethod
    def get_user_addresses(cls, user):
        """
        دریافت همه آدرس‌های فعال کاربر

        Args:
            user: کاربر

        Returns:
            QuerySet
        """
        return UserAddress.objects.filter(
            user=user,
            is_active=True,
        ).order_by('-is_default', '-created_at')

    @classmethod
    def validate_gps(cls, latitude: float, longitude: float) -> bool:
        """
        اعتبارسنجی مختصات GPS

        Args:
            latitude: عرض جغرافیایی (-90 to 90)
            longitude: طول جغرافیایی (-180 to 180)

        Returns:
            bool
        """
        if not latitude or not longitude:
            return False

        if not (-90 <= float(latitude) <= 90):
            return False

        if not (-180 <= float(longitude) <= 180):
            return False

        # چک کن توی ایران باشه (حدوداً)
        # ایران: 25°N - 40°N, 44°E - 63°E
        if not (25 <= float(latitude) <= 40):
            return False

        if not (44 <= float(longitude) <= 63):
            return False

        return True

    @classmethod
    def get_address_count(cls, user) -> int:
        """
        تعداد آدرس‌های کاربر

        Args:
            user: کاربر

        Returns:
            int
        """
        return UserAddress.objects.filter(user=user, is_active=True).count()