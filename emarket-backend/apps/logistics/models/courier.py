import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.logistics.enums import CourierType, VehicleType


class Courier(models.Model):
    """
    مدیریت پیک‌ها

    انواع:
    - INTERNAL: پیک‌های خودمون
    - ALOPEYK: API الوپیک
    - SNAPPBOX: API اسنپ باکس
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==================== Basic Info ====================
    courier_type = models.CharField(
        _('Type'),
        max_length=15,
        choices=CourierType.choices,
        default=CourierType.INTERNAL,
        db_index=True
    )

    name = models.CharField(_('Name'), max_length=200)

    # ==================== Contact ====================
    phone = models.CharField(_('Phone'), max_length=15, blank=True)
    email = models.EmailField(_('Email'), blank=True)

    # ==================== Vehicle ====================
    vehicle_type = models.CharField(
        _('Vehicle Type'),
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.MOTORCYCLE
    )

    vehicle_plate = models.CharField(
        _('Vehicle Plate'),
        max_length=10,
        blank=True
    )

    # ==================== Internal Courier ====================
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courier_profile',
        verbose_name=_('User Account'),
        limit_choices_to={'role': 'courier'}
    )

    national_code = models.CharField(_('National Code'), max_length=10, blank=True)

    is_active = models.BooleanField(_('Active'), default=True)
    is_available = models.BooleanField(_('Available'), default=True)

    # ==================== Current Location ====================
    current_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)

    # ==================== API Integration ====================
    api_key = models.CharField(_('API Key'), max_length=500, blank=True)
    api_secret = models.CharField(_('API Secret'), max_length=500, blank=True)
    webhook_url = models.URLField(_('Webhook URL'), blank=True)

    extra_config = models.JSONField(_('Extra Config'), default=dict, blank=True)

    # ==================== Rating ====================
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'couriers'
        verbose_name = _('Courier')
        verbose_name_plural = _('Couriers')
        ordering = ['-is_available', '-rating']

    def __str__(self):
        return f"🛵 {self.name} ({self.get_courier_type_display()})"

    @property
    def success_rate(self):
        if self.total_deliveries > 0:
            return round((self.successful_deliveries / self.total_deliveries) * 100, 1)
        return 0