import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.stock.enums import WarehouseType, WarehouseScope


class Warehouse(models.Model):
    """
    مدل انبار

    سلسله‌مراتب:
    - انبار اصلی (Main)
    - انبار فرعی (Sub) ← parent = Main
    - انبار تخصصی (Specialized)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Basic Info ====================
    name = models.CharField(
        _('Warehouse Name'),
        max_length=200,
        db_index=True
    )

    code = models.CharField(
        _('Warehouse Code'),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_('Unique code: WH-MAIN-001')
    )

    warehouse_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=WarehouseType.choices,
        default=WarehouseType.MAIN,
        db_index=True
    )

    scope = models.CharField(
        _('Scope'),
        max_length=20,
        choices=WarehouseScope.choices,
        default=WarehouseScope.GENERAL,
        help_text=_('General or Specialized hardware')
    )

    # ==================== Hierarchy ====================
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_warehouses',
        verbose_name=_('Parent Warehouse'),
        help_text=_('Leave empty for main warehouse')
    )

    # ==================== Location ====================
    address = models.TextField(
        _('Address'),
        blank=True
    )

    latitude = models.DecimalField(
        _('Latitude'),
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text=_('GPS Latitude')
    )

    longitude = models.DecimalField(
        _('Longitude'),
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text=_('GPS Longitude')
    )

    # ==================== Contact ====================
    phone = models.CharField(
        _('Phone'),
        max_length=15,
        blank=True
    )

    email = models.EmailField(
        _('Email'),
        blank=True
    )

    # ==================== Management ====================
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_warehouses',
        verbose_name=_('Warehouse Manager'),
        limit_choices_to={'role__in': ['super_admin', 'stock_keeper']}
    )

    staff = models.ManyToManyField(
        User,
        blank=True,
        related_name='warehouses',
        verbose_name=_('Warehouse Staff'),
        limit_choices_to={'role__in': ['stock_keeper', 'accountant']}
    )

    # ==================== Capacity ====================
    capacity = models.PositiveIntegerField(
        _('Capacity'),
        default=0,
        help_text=_('Maximum number of items')
    )

    current_items = models.PositiveIntegerField(
        _('Current Items'),
        default=0,
        help_text=_('Current number of items')
    )

    # ==================== Status ====================
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        db_index=True
    )

    is_public = models.BooleanField(
        _('Public'),
        default=False,
        help_text=_('Visible to customers')
    )

    description = models.TextField(
        _('Description'),
        blank=True
    )

    # ==================== Specialization ====================
    specialized_hardware = models.CharField(
        _('Specialized Hardware'),
        max_length=200,
        blank=True,
        help_text=_('If scope is specialized, specify hardware type')
    )

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'warehouses'
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')
        ordering = ['warehouse_type', 'name']
        indexes = [
            models.Index(fields=['warehouse_type', 'is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_main(self):
        return self.warehouse_type == WarehouseType.MAIN

    @property
    def is_sub(self):
        return self.warehouse_type == WarehouseType.SUB

    @property
    def is_specialized(self):
        return self.warehouse_type == WarehouseType.SPECIALIZED

    @property
    def location(self):
        """موقعیت جغرافیایی"""
        if self.latitude and self.longitude:
            return {
                'lat': float(self.latitude),
                'lng': float(self.longitude),
            }
        return None

    @property
    def full_address(self):
        """آدرس کامل"""
        if self.location:
            return f"{self.address} ({self.latitude}, {self.longitude})"
        return self.address

    @property
    def sub_warehouses_count(self):
        return self.sub_warehouses.count()

    def get_hierarchy(self):
        """دریافت سلسله‌مراتب"""
        hierarchy = [self]
        current = self
        while current.parent:
            hierarchy.insert(0, current.parent)
            current = current.parent
        return hierarchy