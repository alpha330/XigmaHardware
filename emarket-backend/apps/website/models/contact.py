import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """پیام‌های تماس با ما"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(_('Name'), max_length=150)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=15, blank=True)
    subject = models.CharField(_('Subject'), max_length=300)
    message = models.TextField(_('Message'))

    is_read = models.BooleanField(_('Read'), default=False)
    is_replied = models.BooleanField(_('Replied'), default=False)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}: {self.subject[:50]}"


class Newsletter(models.Model):
    """عضویت در خبرنامه"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(_('Email'), unique=True)
    is_active = models.BooleanField(_('Active'), default=True)

    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'newsletter_subscribers'

    def __str__(self):
        return self.email