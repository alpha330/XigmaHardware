import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.accounts.managers import UserManager
from apps.accounts.enums import UserRole, VerificationType
from apps.accounts.validators import validate_iranian_phone


class User(AbstractBaseUser, PermissionsMixin):
    """
    مدل اصلی کاربر با قابلیت ثبت‌نام با ایمیل یا موبایل
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    
    # فیلدهای احراز هویت
    email = models.EmailField(
        _('Email'),
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text=_('Required if registering with email')
    )
    
    mobile = models.CharField(
        _('Mobile'),
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_iranian_phone],
        db_index=True,
        help_text=_('Required if registering with mobile')
    )
    
    # روش ثبت‌نام
    registration_method = models.CharField(
        _('Registration Method'),
        max_length=10,
        choices=VerificationType.choices,
        null=True,
        blank=True,
        help_text=_('How user registered: email or mobile')
    )
    
    # وضعیت‌های تایید
    is_email_verified = models.BooleanField(
        _('Email Verified'),
        default=False,
        help_text=_('Whether email has been verified')
    )
    
    is_mobile_verified = models.BooleanField(
        _('Mobile Verified'),
        default=False,
        help_text=_('Whether mobile has been verified')
    )
    
    # نقش کاربر
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.default(),
        db_index=True
    )
    
    # وضعیت کلی حساب
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        db_index=True
    )
    
    is_staff = models.BooleanField(
        _('Staff Status'),
        default=False
    )
    
    # اطلاعات امنیتی
    last_login_ip = models.GenericIPAddressField(
        _('Last Login IP'),
        null=True,
        blank=True
    )
    
    last_login_method = models.CharField(
        _('Last Login Method'),
        max_length=10,
        choices=VerificationType.choices,
        null=True,
        blank=True
    )
    
    failed_login_attempts = models.PositiveIntegerField(
        _('Failed Login Attempts'),
        default=0
    )
    
    locked_until = models.DateTimeField(
        _('Locked Until'),
        null=True,
        blank=True
    )
    
    # تایم‌استمپ‌ها
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )
    
    last_login = models.DateTimeField(
        _('Last Login'),
        null=True,
        blank=True
    )
    
    last_activity = models.DateTimeField(
        _('Last Activity'),
        default=timezone.now
    )
    
    # استفاده از منیجر سفارشی
    objects = UserManager()
    
    # تنظیمات احراز هویت
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'mobile']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['is_email_verified', 'is_mobile_verified']),
        ]
    
    def __str__(self):
        return self.get_display_name()
    
    def get_display_name(self):
        """نمایش نام کاربر بر اساس اطلاعات موجود"""
        if hasattr(self, 'profile'):
            if self.profile.is_legal and self.profile.company_name:
                return self.profile.company_name
            elif self.profile.full_name:
                return self.profile.full_name
        
        return self.email or self.mobile or str(self.id)
    
    def get_short_name(self):
        """نام کوتاه کاربر"""
        if hasattr(self, 'profile') and self.profile.full_name:
            return self.profile.full_name.split()[0]
        return self.get_display_name()
    
    @property
    def is_verified(self):
        """
        بررسی می‌کند که آیا کاربر تایید شده است
        اگر با ایمیل ثبت‌نام کرده، ایمیل باید تایید شود
        اگر با موبایل ثبت‌نام کرده، موبایل باید تایید شود
        اگر با هر دو ثبت‌نام کرده، هر دو باید تایید شوند
        """
        if self.registration_method == VerificationType.EMAIL:
            return self.is_email_verified
        elif self.registration_method == VerificationType.MOBILE:
            return self.is_mobile_verified
        elif self.email and self.mobile:
            return self.is_email_verified and self.is_mobile_verified
        elif self.email:
            return self.is_email_verified
        elif self.mobile:
            return self.is_mobile_verified
        return False
    
    @property
    def is_locked(self):
        """بررسی قفل بودن حساب کاربری"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def get_primary_contact(self):
        """دریافت راه ارتباطی اصلی"""
        if self.mobile:
            return self.mobile
        return self.email
    
    def verify_email(self):
        """تایید ایمیل کاربر"""
        self.is_email_verified = True
        self.save(update_fields=['is_email_verified', 'updated_at'])
    
    def verify_mobile(self):
        """تایید موبایل کاربر"""
        self.is_mobile_verified = True
        self.save(update_fields=['is_mobile_verified', 'updated_at'])
    
    def increment_failed_login(self):
        """افزایش تعداد تلاش‌های ناموفق"""
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
            self.failed_login_attempts = 0
        
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def reset_failed_login(self):
        """بازنشانی تلاش‌های ناموفق"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])