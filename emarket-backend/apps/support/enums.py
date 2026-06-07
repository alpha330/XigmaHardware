from django.db import models
from django.utils.translation import gettext_lazy as _


class TicketStatus(models.TextChoices):
    OPEN = 'open', _('Open')
    IN_PROGRESS = 'in_progress', _('In Progress')
    WAITING_CUSTOMER = 'waiting_customer', _('Waiting for Customer')
    RESOLVED = 'resolved', _('Resolved')
    CLOSED = 'closed', _('Closed')


class TicketPriority(models.TextChoices):
    LOW = 'low', _('Low')
    MEDIUM = 'medium', _('Medium')
    HIGH = 'high', _('High')
    URGENT = 'urgent', _('Urgent')


class TicketCategory(models.TextChoices):
    ORDER = 'order', _('Order Issue')
    PAYMENT = 'payment', _('Payment Problem')
    PRODUCT = 'product', _('Product Inquiry')
    WARRANTY = 'warranty', _('Warranty Claim')
    TECHNICAL = 'technical', _('Technical Support')
    ACCOUNT = 'account', _('Account Issue')
    SHIPPING = 'shipping', _('Shipping Problem')
    OTHER = 'other', _('Other')


class WarrantyStatus(models.TextChoices):
    ACTIVE = 'active', _('Active')
    EXPIRED = 'expired', _('Expired')
    CLAIMED = 'claimed', _('Claimed')
    REJECTED = 'rejected', _('Rejected')
    COMPLETED = 'completed', _('Completed')


class ChatStatus(models.TextChoices):
    WAITING = 'waiting', _('Waiting')
    ACTIVE = 'active', _('Active')
    CLOSED = 'closed', _('Closed')