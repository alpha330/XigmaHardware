import uuid
import random
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.accounts.enums import OTPPurpose


class OTPCode(models.Model):
    """
    مدل کدهای یکبار مصرف برای احراز هویت
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
        related_name='otp_codes',
        verbose_name=_('User')
    )

    # کد OTP
    code = models.CharField(
        _('Code'),
        max_length=6
    )

    # هدف از ارسال
    purpose = models.CharField(
        _('Purpose'),
        max_length=20,
        choices=OTPPurpose.choices,
        db_index=True
    )

    # روش ارسال
    sent_via = models.CharField(
        _('Sent Via'),
        max_length=10,
        choices=[('email', 'Email'), ('sms', 'SMS')],
        default='sms'
    )

    # وضعیت
    is_used = models.BooleanField(
        _('Used'),
        default=False,
        db_index=True
    )

    # زمان انقضا
    expires_at = models.DateTimeField(
        _('Expires At')
    )

    # تعداد تلاش‌های ناموفق
    attempts = models.PositiveIntegerField(
        _('Attempts'),
        default=0
    )

    # زمان استفاده
    used_at = models.DateTimeField(
        _('Used At'),
        null=True,
        blank=True
    )

    # زمان ایجاد
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )

    class Meta:
        db_table = 'otp_codes'
        verbose_name = _('OTP Code')
        verbose_name_plural = _('OTP Codes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_used']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"OTP for {self.user.get_display_name()} - {self.purpose}"

    @classmethod
    def generate(cls, user, purpose, sent_via='sms', length=6, validity_minutes=2): # تغییر پیش‌فرض به ۲
        # غیرفعال کردن کدهای قبلی با همین هدف
        cls.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)

        code = ''.join([str(random.randint(0, 9)) for _ in range(length)])

        otp = cls.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            sent_via=sent_via,
            expires_at=timezone.now() + timezone.timedelta(minutes=validity_minutes) # لحاظ شدن ۲ دقیقه
        )
        return otp

    def is_valid(self):
        """
        بررسی اعتبار کد OTP
        """
        if self.is_used:
            return False

        if timezone.now() > self.expires_at:
            return False

        if self.attempts >= 3:
            return False

        return True

    def verify(self, code):
        """
        تایید کد OTP
        """
        self.attempts += 1

        if not self.is_valid():
            self.save(update_fields=['attempts'])
            return False

        if self.code != code:
            self.save(update_fields=['attempts'])
            return False

        # تایید موفق
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at', 'attempts'])

        return True