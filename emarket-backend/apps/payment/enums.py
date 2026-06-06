from django.db import models
from django.utils.translation import gettext_lazy as _


class GatewayType(models.TextChoices):
    """انواع درگاه پرداخت"""
    PAYPING = 'payping', _('PayPing')
    ZARINPAL = 'zarinpal', _('ZarinPal')
    CRYPTO = 'crypto', _('Cryptocurrency')
    CARD_TO_CARD = 'card_to_card', _('Card to Card')
    CUSTOM = 'custom', _('Custom Gateway')


class GatewayMode(models.TextChoices):
    """حالت درگاه"""
    TEST = 'test', _('Test/Sandbox')
    LIVE = 'live', _('Live/Production')


class PaymentStatus(models.TextChoices):
    """وضعیت پرداخت"""
    PENDING = 'pending', _('Pending')
    REDIRECTED = 'redirected', _('Redirected to Gateway')
    VERIFIED = 'verified', _('Verified')
    FAILED = 'failed', _('Failed')
    CANCELLED = 'cancelled', _('Cancelled')
    REFUNDED = 'refunded', _('Refunded')