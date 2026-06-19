import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.logistics.enums import ShipmentStatus


class Shipment(models.Model):
    """
    مدیریت ارسال‌ها

    هر ارسال شامل:
    - آدرس مبدا (انبار)
    - آدرس مقصد (کاربر)
    - پیک
    - وضعیت
    - هزینه
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ==================== Relations ====================
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shipments',
        verbose_name=_('Customer')
    )

    invoice = models.ForeignKey(
        'financial.Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments',
        verbose_name=_('Invoice')
    )

    # ==================== Addresses ====================
    origin_warehouse = models.ForeignKey(
        'stock.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        related_name='outgoing_shipments',
        verbose_name=_('Origin Warehouse')
    )

    origin_address = models.TextField(_('Origin Address'), blank=True)
    origin_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    origin_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    destination_address = models.ForeignKey(
        'logistics.UserAddress',
        on_delete=models.SET_NULL,
        null=True,
        related_name='shipments',
        verbose_name=_('Destination Address')
    )

    destination_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    destination_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # ==================== Courier ====================
    courier = models.ForeignKey(
        'logistics.Courier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments',
        verbose_name=_('Courier')
    )

    courier_tracking_code = models.CharField(
        _('Courier Tracking Code'),
        max_length=100,
        blank=True
    )

    # ==================== Status ====================
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
        db_index=True
    )

    # ==================== Pricing ====================
    shipping_cost = models.DecimalField(
        _('Shipping Cost'),
        max_digits=15,
        decimal_places=2,
        default=0
    )

    courier_cost = models.DecimalField(
        _('Courier Cost'),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_('What we pay to courier')
    )

    customer_cost = models.DecimalField(
        _('Customer Cost'),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_('What customer pays')
    )

    distance_km = models.DecimalField(
        _('Distance (km)'),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )

    estimated_duration = models.PositiveIntegerField(
        _('Estimated Duration (min)'),
        null=True,
        blank=True
    )

    # ==================== Package Info ====================
    package_weight_kg = models.DecimalField(
        _('Weight (kg)'),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    package_description = models.TextField(_('Package Description'), blank=True)

    # ==================== Notes ====================
    notes = models.TextField(_('Notes'), blank=True)
    courier_notes = models.TextField(_('Courier Notes'), blank=True)

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'shipments'
        verbose_name = _('Shipment')
        verbose_name_plural = _('Shipments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['courier', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"📦 Shipment #{str(self.id)[:8]} - {self.get_status_display()}"

    @property
    def is_delivered(self):
        return self.status == ShipmentStatus.DELIVERED

    @property
    def can_cancel(self):
        return self.status in [ShipmentStatus.PENDING, ShipmentStatus.ASSIGNED]

    def assign_courier(self, courier):
        """تخصیص پیک"""
        self.courier = courier
        self.status = ShipmentStatus.ASSIGNED
        self.assigned_at = __import__('django').utils.timezone.now()
        self.save()

    def mark_picked_up(self):
        self.status = ShipmentStatus.PICKED_UP
        self.picked_up_at = __import__('django').utils.timezone.now()
        self.save()

    def mark_delivered(self):
        self.status = ShipmentStatus.DELIVERED
        self.delivered_at = __import__('django').utils.timezone.now()

        if self.courier:
            self.courier.total_deliveries += 1
            self.courier.successful_deliveries += 1
            self.courier.save()

        self.save()

    def cancel(self):
        self.status = ShipmentStatus.CANCELLED
        self.save()


class ShipmentTracking(models.Model):
    """
    رهگیری وضعیت ارسال (گام به گام)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='tracking_events'
    )

    status = models.CharField(_('Status'), max_length=20, choices=ShipmentStatus.choices)

    description = models.TextField(_('Description'), blank=True)

    location_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shipment_tracking'
        verbose_name = _('Tracking Event')
        verbose_name_plural = _('Tracking Events')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_status_display()} - {self.created_at}"
