import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.payment.enums import GatewayType, GatewayMode


class PaymentGateway(models.Model):
    """
    مدل تنظیمات درگاه پرداخت

    ادمین می‌تونه چندین درگاه با تنظیمات مختلف تعریف کنه
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Basic Info ====================
    name = models.CharField(
        _('Gateway Name'),
        max_length=100,
        help_text=_('e.g., PayPing Main, Crypto BTC')
    )

    gateway_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=GatewayType.choices,
        db_index=True
    )

    mode = models.CharField(
        _('Mode'),
        max_length=10,
        choices=GatewayMode.choices,
        default=GatewayMode.TEST,
        db_index=True
    )

    # ==================== API Credentials ====================
    api_key = models.CharField(
        _('API Key'),
        max_length=500,
        blank=True,
        help_text=_('Token/API Key for PayPing')
    )

    sandbox_api_key = models.CharField(
        _('Sandbox API Key'),
        max_length=500,
        blank=True,
        help_text=_('Test token for sandbox mode')
    )

    merchant_id = models.CharField(
        _('Merchant ID'),
        max_length=200,
        blank=True,
        help_text=_('For ZarinPal or similar')
    )

    # ==================== Crypto ====================
    wallet_address = models.CharField(
        _('Wallet Address'),
        max_length=500,
        blank=True,
        help_text=_('Crypto wallet address')
    )

    network = models.CharField(
        _('Network'),
        max_length=50,
        blank=True,
        help_text=_('e.g., TRC20, ERC20, BEP20')
    )

    # ==================== Callback ====================
    callback_url = models.URLField(
        _('Callback URL'),
        blank=True,
        help_text=_('Override default callback URL')
    )

    # ==================== Limits ====================
    min_amount = models.DecimalField(
        _('Minimum Amount'),
        max_digits=15,
        decimal_places=2,
        default=1000,
        help_text=_('Minimum payment amount in Rials')
    )

    max_amount = models.DecimalField(
        _('Maximum Amount'),
        max_digits=15,
        decimal_places=2,
        default=500000000,
        help_text=_('Maximum payment amount in Rials')
    )

    # ==================== Status ====================
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)
    is_default = models.BooleanField(_('Default Gateway'), default=False)

    priority = models.PositiveIntegerField(
        _('Priority'),
        default=0,
        help_text=_('Higher number = higher priority')
    )

    # ==================== Config ====================
    extra_config = models.JSONField(
        _('Extra Configuration'),
        default=dict,
        blank=True,
        help_text=_('Additional gateway-specific settings')
    )

    description = models.TextField(_('Description'), blank=True)

    # ==================== Timestamps ====================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_gateways'
        verbose_name = _('Payment Gateway')
        verbose_name_plural = _('Payment Gateways')
        ordering = ['-priority', '-is_default', 'name']
        indexes = [
            models.Index(fields=['gateway_type', 'mode', 'is_active']),
            models.Index(fields=['is_default']),
        ]

    def __str__(self):
        mode_icon = '🧪' if self.mode == GatewayMode.TEST else '🟢'
        return f"{mode_icon} {self.name} ({self.get_gateway_type_display()})"

    @property
    def effective_api_key(self):
        """API Key مناسب بر اساس mode"""
        if self.mode == GatewayMode.TEST and self.sandbox_api_key:
            return self.sandbox_api_key
        return self.api_key

    @property
    def is_payping(self):
        return self.gateway_type == GatewayType.PAYPING

    @property
    def is_crypto(self):
        return self.gateway_type == GatewayType.CRYPTO

    def save(self, *args, **kwargs):
        """اگر default هست، بقیه رو غیرفعال کن"""
        if self.is_default:
            PaymentGateway.objects.filter(is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)