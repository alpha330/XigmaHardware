import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.stock.enums import InventoryStatus


class InventoryItem(models.Model):
    """
    موجودی یک محصول در یک انبار خاص

    رابطه: Warehouse ← InventoryItem → Product
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Relations ====================
    warehouse = models.ForeignKey(
        'stock.Warehouse',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_('Warehouse')
    )

    product = models.ForeignKey(
        'stock.Product',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_('Product')
    )

    # ==================== Quantity ====================
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        default=0,
        help_text=_('Total quantity in this warehouse')
    )

    reserved_quantity = models.PositiveIntegerField(
        _('Reserved Quantity'),
        default=0,
        help_text=_('Quantity reserved for orders')
    )

    minimum_quantity = models.PositiveIntegerField(
        _('Minimum Quantity'),
        default=0,
        help_text=_('Alert when below this level')
    )

    # ==================== Location in Warehouse ====================
    shelf = models.CharField(
        _('Shelf/Rack'),
        max_length=50,
        blank=True,
        help_text=_('Shelf or rack number')
    )

    aisle = models.CharField(
        _('Aisle'),
        max_length=50,
        blank=True
    )

    section = models.CharField(
        _('Section'),
        max_length=50,
        blank=True
    )

    location_barcode = models.CharField(
        _('Location Barcode'),
        max_length=100,
        blank=True,
        unique=True,
        null=True
    )

    # ==================== Status ====================
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=InventoryStatus.choices,
        default=InventoryStatus.IN_STOCK,
        db_index=True
    )

    # ==================== Batch Info ====================
    batch_number = models.CharField(
        _('Batch Number'),
        max_length=100,
        blank=True
    )

    received_date = models.DateField(
        _('Received Date'),
        null=True,
        blank=True
    )

    expiry_date = models.DateField(
        _('Expiry Date'),
        null=True,
        blank=True,
        help_text=_('For items with shelf life')
    )

    # ==================== Notes ====================
    notes = models.TextField(_('Notes'), blank=True)

    # ==================== Audit ====================
    last_checked_at = models.DateTimeField(
        _('Last Stock Check'),
        null=True,
        blank=True
    )

    last_checked_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_checks'
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'inventory_items'
        verbose_name = _('Inventory Item')
        verbose_name_plural = _('Inventory Items')
        unique_together = [
            ['warehouse', 'product', 'batch_number'],
        ]
        ordering = ['warehouse', 'product__sku']
        indexes = [
            models.Index(fields=['warehouse', 'status']),
            models.Index(fields=['product', 'status']),
            models.Index(fields=['quantity']),
        ]

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.code} - Qty: {self.quantity}"

    @property
    def available_quantity(self):
        """موجودی قابل استفاده"""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_low_stock(self):
        """هشدار موجودی کم"""
        return self.available_quantity <= self.minimum_quantity

    @property
    def location(self):
        """موقعیت فیزیکی در انبار"""
        parts = [self.section, self.aisle, self.shelf]
        return ' > '.join([p for p in parts if p]) or '-'

    def reserve(self, qty):
        """رزرو موجودی"""
        if qty > self.available_quantity:
            raise ValueError(_('Not enough stock to reserve'))
        self.reserved_quantity += qty
        self.save(update_fields=['reserved_quantity', 'updated_at'])

    def unreserve(self, qty):
        """لغو رزرو"""
        if qty > self.reserved_quantity:
            raise ValueError(_('Not enough reserved stock'))
        self.reserved_quantity -= qty
        self.save(update_fields=['reserved_quantity', 'updated_at'])

    def add_stock(self, qty):
        """افزایش موجودی"""
        self.quantity += qty
        self.last_checked_at = models.functions.Now()
        self.save(update_fields=['quantity', 'last_checked_at', 'updated_at'])

    def remove_stock(self, qty):
        """کاهش موجودی"""
        if qty > self.available_quantity:
            raise ValueError(_('Not enough stock'))
        self.quantity -= qty
        self.save(update_fields=['quantity', 'updated_at'])


class StockMovement(models.Model):
    """
    رهگیری جابجایی موجودی
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='movements'
    )

    movement_type = models.CharField(
        _('Movement Type'),
        max_length=30,
        choices=[
            ('in', _('Stock In')),
            ('out', _('Stock Out')),
            ('transfer', _('Transfer')),
            ('reserve', _('Reserved')),
            ('unreserve', _('Unreserved')),
            ('adjustment', _('Adjustment')),
            ('return', _('Return')),
            ('damaged', _('Damaged')),
        ]
    )

    quantity = models.IntegerField(_('Quantity'))

    # Source/Destination
    from_warehouse = models.ForeignKey(
        'stock.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_movements'
    )

    to_warehouse = models.ForeignKey(
        'stock.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_movements'
    )

    reference = models.CharField(
        _('Reference'),
        max_length=200,
        blank=True,
        help_text=_('Order number, transfer ID, etc.')
    )

    notes = models.TextField(_('Notes'), blank=True)

    performed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_movements'
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'stock_movements'
        verbose_name = _('Stock Movement')
        verbose_name_plural = _('Stock Movements')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_item', 'created_at']),
            models.Index(fields=['movement_type']),
        ]

    def __str__(self):
        return f"{self.movement_type}: {self.quantity} units - {self.created_at}"