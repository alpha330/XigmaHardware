import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User
from apps.support.enums import WarrantyStatus


class Warranty(models.Model):
    """گارانتی محصولات فروخته شده"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    warranty_number = models.CharField(_('Warranty #'), max_length=30, unique=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warranties')
    product = models.ForeignKey('stock.Product', on_delete=models.CASCADE, related_name='warranties')
    invoice = models.ForeignKey('financial.Invoice', on_delete=models.SET_NULL, null=True, related_name='warranties')

    status = models.CharField(_('Status'), max_length=20, choices=WarrantyStatus.choices, default=WarrantyStatus.ACTIVE)

    # Warranty Period
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    duration_months = models.PositiveIntegerField(_('Duration (months)'))

    # Warranty Details
    serial_number = models.CharField(_('Serial Number'), max_length=100, blank=True)
    warranty_type = models.CharField(_('Type'), max_length=50, default='Manufacturer')
    coverage = models.TextField(_('Coverage Details'), blank=True)
    terms = models.TextField(_('Terms & Conditions'), blank=True)

    # Claim Info
    claim_date = models.DateField(_('Claim Date'), null=True, blank=True)
    claim_description = models.TextField(_('Claim Description'), blank=True)
    resolution = models.TextField(_('Resolution'), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'warranties'
        ordering = ['-created_at']

    def __str__(self):
        return f"Warranty #{self.warranty_number} - {self.product.name[:30]}"

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == WarrantyStatus.ACTIVE and self.end_date >= timezone.now().date()

    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(0, delta.days)
        return 0