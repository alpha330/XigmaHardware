import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.enums import ProfileType
from apps.accounts.validators import (
    validate_national_code,
    validate_national_id,
    validate_economic_code,
    validate_postal_code
)


class Profile(models.Model):
    """
    مدل پروفایل کاربر با قابلیت حقیقی و حقوقی
    هر کاربر دقیقاً یک پروفایل دارد (OneToOne)
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    
    # ارتباط یک به یک با کاربر
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    
    # نوع پروفایل
    profile_type = models.CharField(
        _('Profile Type'),
        max_length=10,
        choices=ProfileType.choices,
        default=ProfileType.default(),
        db_index=True
    )
    
    # فیلدهای مشترک
    avatar = models.ImageField(
        _('Avatar'),
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True
    )
    
    birth_date = models.DateField(
        _('Birth Date'),
        null=True,
        blank=True
    )
    
    # اطلاعات تماس
    tel = models.CharField(
        _('Telephone'),
        max_length=15,
        blank=True,
        help_text=_('Landline phone number')
    )
    
    address = models.TextField(
        _('Address'),
        blank=True
    )
    
    postal_code = models.CharField(
        _('Postal Code'),
        max_length=10,
        blank=True,
        validators=[validate_postal_code],
        help_text=_('10-digit postal code')
    )
    
    # فیلدهای حقیقی (Individual)
    national_code = models.CharField(
        _('National Code'),
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        validators=[validate_national_code],
        help_text=_('10-digit national code for individuals')
    )
    
    # فیلدهای حقوقی (Legal/Company)
    company_name = models.CharField(
        _('Company Name'),
        max_length=200,
        blank=True,
        help_text=_('Required for legal profiles')
    )
    
    national_id = models.CharField(
        _('National ID'),
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        validators=[validate_national_id],
        help_text=_('11-digit national ID for companies')
    )
    
    economic_code = models.CharField(
        _('Economic Code'),
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        validators=[validate_economic_code],
        help_text=_('12-digit economic code for companies')
    )
    
    # وضعیت تایید پروفایل
    is_completed = models.BooleanField(
        _('Profile Completed'),
        default=False,
        help_text=_('Whether profile has all required fields')
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
    
    class Meta:
        db_table = 'profiles'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        indexes = [
            models.Index(fields=['profile_type']),
            models.Index(fields=['national_code']),
            models.Index(fields=['national_id']),
            models.Index(fields=['economic_code']),
        ]
    
    def __str__(self):
        return f"Profile: {self.user.get_display_name()}"
    
    @property
    def is_individual(self):
        """بررسی حقیقی بودن"""
        return self.profile_type == ProfileType.INDIVIDUAL
    
    @property
    def is_legal(self):
        """بررسی حقوقی بودن"""
        return self.profile_type == ProfileType.LEGAL
    
    @property
    def full_name(self):
        """نام کامل برای حقیقی"""
        if self.is_individual:
            user = self.user
            if user.first_name or user.last_name:
                return f"{user.first_name} {user.last_name}".strip()
        return None
    
    def check_completion(self):
        """
        بررسی تکمیل بودن پروفایل بر اساس نوع (حقیقی/حقوقی)
        """
        if self.is_individual:
            # فیلدهای اجباری برای حقیقی
            required_fields = [
                self.national_code,
            ]
        else:  # Legal
            # فیلدهای اجباری برای حقوقی
            required_fields = [
                self.company_name,
                self.national_id,
                self.economic_code,
            ]
        
        return all(required_fields)
    
    def complete_profile(self):
        """تکمیل خودکار پروفایل اگر همه فیلدها پر باشند"""
        self.is_completed = self.check_completion()
        if self.is_completed:
            self.save(update_fields=['is_completed'])
        return self.is_completed
    
    def switch_to_legal(self, company_name, national_id, economic_code):
        """تغییر نوع پروفایل به حقوقی"""
        self.profile_type = ProfileType.LEGAL
        self.company_name = company_name
        self.national_id = national_id
        self.economic_code = economic_code
        self.national_code = None  # پاک کردن فیلد حقیقی
        self.save()
    
    def switch_to_individual(self, national_code):
        """تغییر نوع پروفایل به حقیقی"""
        self.profile_type = ProfileType.INDIVIDUAL
        self.national_code = national_code
        self.company_name = ''  # پاک کردن فیلدهای حقوقی
        self.national_id = None
        self.economic_code = None
        self.save()