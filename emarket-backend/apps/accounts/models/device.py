import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserDevice(models.Model):
    """
    مدل دستگاه‌های کاربر برای رهگیری و امنیت
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name=_('User')
    )
    
    # اطلاعات دستگاه
    device_name = models.CharField(
        _('Device Name'),
        max_length=200,
        blank=True
    )
    
    device_type = models.CharField(
        _('Device Type'),
        max_length=50,
        blank=True,
        help_text=_('e.g., Desktop, Mobile, Tablet')
    )
    
    operating_system = models.CharField(
        _('Operating System'),
        max_length=100,
        blank=True
    )
    
    browser = models.CharField(
        _('Browser'),
        max_length=100,
        blank=True
    )
    
    browser_version = models.CharField(
        _('Browser Version'),
        max_length=50,
        blank=True
    )
    
    # اطلاعات شبکه
    ip_address = models.GenericIPAddressField(
        _('IP Address'),
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        _('User Agent'),
        blank=True
    )
    
    # موقعیت جغرافیایی
    country = models.CharField(
        _('Country'),
        max_length=100,
        blank=True
    )
    
    city = models.CharField(
        _('City'),
        max_length=100,
        blank=True
    )
    
    # توکن برای پوش نوتیفیکیشن
    device_token = models.CharField(
        _('Device Token'),
        max_length=500,
        blank=True,
        help_text=_('FCM/APNS token for push notifications')
    )
    
    # وضعیت دستگاه
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        db_index=True
    )
    
    is_trusted = models.BooleanField(
        _('Trusted'),
        default=False
    )
    
    # زمان‌ها
    last_used = models.DateTimeField(
        _('Last Used'),
        auto_now=True
    )
    
    first_seen = models.DateTimeField(
        _('First Seen'),
        auto_now_add=True
    )
    
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'user_devices'
        verbose_name = _('User Device')
        verbose_name_plural = _('User Devices')
        unique_together = [
            ['user', 'device_token'],
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['last_used']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.device_name or 'Unknown Device'}"
    
    def get_device_info(self):
        """دریافت اطلاعات کامل دستگاه"""
        return {
            'name': self.device_name,
            'type': self.device_type,
            'os': self.operating_system,
            'browser': f"{self.browser} {self.browser_version}",
            'ip': str(self.ip_address) if self.ip_address else None,
            'location': f"{self.city}, {self.country}" if self.city else None,
        }
    
    def trust(self):
        """اعتماد به دستگاه"""
        self.is_trusted = True
        self.save(update_fields=['is_trusted'])
    
    def revoke_trust(self):
        """لغو اعتماد به دستگاه"""
        self.is_trusted = False
        self.save(update_fields=['is_trusted'])