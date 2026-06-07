import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.logistics.enums import AddressType


class UserAddress(models.Model):
    """
    آدرس‌های کاربران

    ویژگی‌ها:
    - آدرس کامل با GPS
    - قابلیت انتخاب روی نقشه
    - چندین آدرس برای هر کاربر
    - آدرس پیش‌فرض
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==================== Owner ====================
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('User')
    )

    # ==================== Address Info ====================
    address_type = models.CharField(
        _('Type'),
        max_length=15,
        choices=AddressType.choices,
        default=AddressType.HOME,
        db_index=True
    )

    title = models.CharField(
        _('Address Title'),
        max_length=100,
        help_text=_('e.g., Home, Office, Parent\'s House')
    )

    # ==================== Recipient ====================
    recipient_name = models.CharField(
        _('Recipient Name'),
        max_length=150
    )

    recipient_mobile = models.CharField(
        _('Recipient Mobile'),
        max_length=11
    )

    # ==================== Address ====================
    country = models.CharField(
        _('Country'),
        max_length=50,
        default='Iran'
    )

    province = models.CharField(
        _('Province'),
        max_length=100
    )

    city = models.CharField(
        _('City'),
        max_length=100
    )

    district = models.CharField(
        _('District'),
        max_length=100,
        blank=True
    )

    postal_code = models.CharField(
        _('Postal Code'),
        max_length=10,
        blank=True
    )

    address_line = models.TextField(
        _('Address'),
        help_text=_('Full street address')
    )

    # ==================== Location Details ====================
    plaque = models.CharField(
        _('Plaque'),
        max_length=10,
        blank=True,
        null=True
    )

    unit = models.CharField(
        _('Unit'),
        max_length=10,
        blank=True,
        null=True
    )

    floor = models.CharField(
        _('Floor'),
        max_length=10,
        blank=True,
        null=True
    )

    # ==================== GPS Coordinates ====================
    latitude = models.DecimalField(
        _('Latitude'),
        max_digits=10,
        decimal_places=7,
        help_text=_('From Google Maps')
    )

    longitude = models.DecimalField(
        _('Longitude'),
        max_digits=10,
        decimal_places=7,
        help_text=_('From Google Maps')
    )

    # ==================== Google Place Info ====================
    google_place_id = models.CharField(
        _('Google Place ID'),
        max_length=255,
        blank=True
    )

    google_formatted_address = models.TextField(
        _('Google Formatted Address'),
        blank=True
    )

    # ==================== Status ====================
    is_default = models.BooleanField(
        _('Default'),
        default=False,
        db_index=True
    )

    is_active = models.BooleanField(
        _('Active'),
        default=True,
        db_index=True
    )

    is_verified = models.BooleanField(
        _('Verified'),
        default=False,
        help_text=_('Verified by courier')
    )

    # ==================== Notes ====================
    delivery_instructions = models.TextField(
        _('Delivery Instructions'),
        blank=True,
        help_text=_('e.g., Ring buzzer #3, Leave at door')
    )

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_addresses'
        verbose_name = _('User Address')
        verbose_name_plural = _('User Addresses')
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient_name} ({self.city})"

    @property
    def full_address(self):
        """آدرس کامل"""
        parts = [
            self.province,
            self.city,
            self.district,
            self.address_line,
        ]
        if self.plaque:
            parts.append(f'پلاک {self.plaque}')
        if self.unit:
            parts.append(f'واحد {self.unit}')
        if self.floor:
            parts.append(f'طبقه {self.floor}')

        return '، '.join([p for p in parts if p])

    @property
    def gps_url(self):
        """لینک Google Maps"""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

    def set_as_default(self):
        """تنظیم به عنوان آدرس پیش‌فرض"""
        UserAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        self.is_default = True
        self.save(update_fields=['is_default'])