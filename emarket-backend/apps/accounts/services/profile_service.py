import logging
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from apps.accounts.enums import ProfileType
from apps.accounts.validators import (
    validate_national_code,
    validate_national_id,
    validate_economic_code,
)

logger = logging.getLogger(__name__)


class ProfileService:
    """
    سرویس مدیریت پروفایل کاربران
    
    عملیات‌های اصلی:
    - ایجاد خودکار پروفایل
    - به‌روزرسانی پروفایل
    - تغییر نوع پروفایل (حقیقی ↔ حقوقی)
    - بررسی تکمیل بودن پروفایل
    - آپلود آواتار
    """
    
    @classmethod
    @transaction.atomic
    def create_profile(cls, user):
        """
        ایجاد خودکار پروفایل برای کاربر جدید
        
        Args:
            user: کاربر جدید
        
        Returns:
            Profile: پروفایل ایجاد شده
        """
        from apps.accounts.models import Profile
        
        profile = Profile.objects.create(
            user=user,
            profile_type=ProfileType.default()
        )
        
        logger.info(f"Profile created for user: {user.email or user.mobile}")
        
        return profile
    
    @classmethod
    @transaction.atomic
    def update_profile(cls, profile, data):
        """
        به‌روزرسانی پروفایل کاربر
        
        Args:
            profile: نمونه پروفایل
            data: دیکشنری داده‌های جدید
        
        Returns:
            Profile: پروفایل به‌روزرسانی شده
        """
        # فیلدهای عمومی قابل ویرایش
        common_fields = [
            'avatar', 'birth_date', 'tel', 
            'address', 'postal_code'
        ]
        
        # فیلدهای مخصوص حقیقی
        individual_fields = ['national_code']
        
        # فیلدهای مخصوص حقوقی
        legal_fields = ['company_name', 'national_id', 'economic_code']
        
        # به‌روزرسانی فیلدهای عمومی
        for field in common_fields:
            if field in data:
                # اگر آواتار است و None ارسال شده، حذف آواتار قبلی
                if field == 'avatar' and data[field] is None and profile.avatar:
                    profile.avatar.delete(save=False)
                setattr(profile, field, data[field])
        
        # به‌روزرسانی فیلدهای مخصوص بر اساس نوع پروفایل
        if profile.is_individual:
            for field in individual_fields:
                if field in data:
                    # اعتبارسنجی کد ملی
                    if field == 'national_code' and data[field]:
                        validate_national_code(data[field])
                    setattr(profile, field, data[field])
        else:
            for field in legal_fields:
                if field in data:
                    # اعتبارسنجی فیلدهای حقوقی
                    if field == 'national_id' and data[field]:
                        validate_national_id(data[field])
                    elif field == 'economic_code' and data[field]:
                        validate_economic_code(data[field])
                    setattr(profile, field, data[field])
        
        # بررسی تکمیل بودن پروفایل
        profile.is_completed = cls.check_completion(profile)
        
        profile.save()
        
        logger.info(
            f"Profile updated for user: {profile.user.email or profile.user.mobile}"
        )
        
        return profile
    
    @classmethod
    @transaction.atomic
    def switch_to_legal(cls, profile, company_name, national_id, economic_code):
        """
        تغییر پروفایل از حقیقی به حقوقی
        
        Args:
            profile: پروفایل کاربر
            company_name: نام شرکت
            national_id: شناسه ملی
            economic_code: کد اقتصادی
        
        Returns:
            Profile: پروفایل به‌روزرسانی شده
        
        Raises:
            ValueError: اگر پروفایل قبلاً حقوقی باشد
        """
        if profile.is_legal:
            raise ValueError(_('Profile is already legal.'))
        
        # اعتبارسنجی
        if not company_name:
            raise ValueError(_('Company name is required.'))
        
        validate_national_id(national_id)
        validate_economic_code(economic_code)
        
        # بررسی یکتایی شناسه ملی و کد اقتصادی
        from apps.accounts.models import Profile
        
        if Profile.objects.filter(national_id=national_id).exclude(id=profile.id).exists():
            raise ValueError(_('This national ID is already registered.'))
        
        if Profile.objects.filter(economic_code=economic_code).exclude(id=profile.id).exists():
            raise ValueError(_('This economic code is already registered.'))
        
        # تغییر نوع پروفایل
        profile.profile_type = ProfileType.LEGAL
        profile.company_name = company_name
        profile.national_id = national_id
        profile.economic_code = economic_code
        
        # پاک کردن فیلدهای حقیقی
        profile.national_code = None
        
        # بررسی تکمیل بودن
        profile.is_completed = cls.check_completion(profile)
        
        profile.save()
        
        logger.info(
            f"Profile switched to legal: "
            f"{profile.user.email or profile.user.mobile} -> {company_name}"
        )
        
        return profile
    
    @classmethod
    @transaction.atomic
    def switch_to_individual(cls, profile, national_code):
        """
        تغییر پروفایل از حقوقی به حقیقی
        
        Args:
            profile: پروفایل کاربر
            national_code: کد ملی
        
        Returns:
            Profile: پروفایل به‌روزرسانی شده
        
        Raises:
            ValueError: اگر پروفایل قبلاً حقیقی باشد
        """
        if profile.is_individual:
            raise ValueError(_('Profile is already individual.'))
        
        # اعتبارسنجی
        validate_national_code(national_code)
        
        # بررسی یکتایی کد ملی
        from apps.accounts.models import Profile
        if Profile.objects.filter(national_code=national_code).exclude(id=profile.id).exists():
            raise ValueError(_('This national code is already registered.'))
        
        # تغییر نوع پروفایل
        profile.profile_type = ProfileType.INDIVIDUAL
        profile.national_code = national_code
        
        # پاک کردن فیلدهای حقوقی
        profile.company_name = ''
        profile.national_id = None
        profile.economic_code = None
        
        # بررسی تکمیل بودن
        profile.is_completed = cls.check_completion(profile)
        
        profile.save()
        
        logger.info(
            f"Profile switched to individual: "
            f"{profile.user.email or profile.user.mobile}"
        )
        
        return profile
    
    @classmethod
    def check_completion(cls, profile):
        """
        بررسی تکمیل بودن پروفایل
        
        Args:
            profile: پروفایل کاربر
        
        Returns:
            bool: آیا پروفایل تکمیل است؟
        """
        if profile.is_individual:
            # فیلدهای اجباری برای حقیقی
            required_fields = [
                profile.national_code,
                profile.address,
                profile.postal_code,
            ]
        else:
            # فیلدهای اجباری برای حقوقی
            required_fields = [
                profile.company_name,
                profile.national_id,
                profile.economic_code,
                profile.address,
                profile.postal_code,
            ]
        
        # همه فیلدهای اجباری باید پر باشند (نه None و نه رشته خالی)
        return all(field for field in required_fields)
    
    @classmethod
    def calculate_completion_percentage(cls, profile):
        """
        محاسبه درصد تکمیل پروفایل
        
        Args:
            profile: پروفایل کاربر
        
        Returns:
            int: درصد تکمیل (0-100)
        """
        if profile.is_individual:
            # فیلدهای حقیقی با وزن‌های مختلف
            fields = {
                'national_code': 25,      # ضروری
                'address': 20,            # ضروری
                'postal_code': 15,        # ضروری
                'tel': 10,                # اختیاری
                'birth_date': 10,         # اختیاری
                'avatar': 10,             # اختیاری
            }
        else:
            # فیلدهای حقوقی با وزن‌های مختلف
            fields = {
                'company_name': 20,       # ضروری
                'national_id': 20,        # ضروری
                'economic_code': 15,      # ضروری
                'address': 15,            # ضروری
                'postal_code': 10,        # ضروری
                'tel': 10,                # اختیاری
                'avatar': 10,             # اختیاری
            }
        
        percentage = 0
        for field, weight in fields.items():
            value = getattr(profile, field)
            if value and value != '':  # رشته خالی هم حساب نشه
                percentage += weight
        
        return min(percentage, 100)  # حداکثر 100%
    
    @classmethod
    def get_missing_fields(cls, profile):
        """
        دریافت لیست فیلدهای تکمیل نشده
        
        Args:
            profile: پروفایل کاربر
        
        Returns:
            list: لیست فیلدهای missing
        """
        missing = []
        
        if profile.is_individual:
            required = {
                'national_code': _('National Code'),
                'address': _('Address'),
                'postal_code': _('Postal Code'),
            }
        else:
            required = {
                'company_name': _('Company Name'),
                'national_id': _('National ID'),
                'economic_code': _('Economic Code'),
                'address': _('Address'),
                'postal_code': _('Postal Code'),
            }
        
        for field, label in required.items():
            value = getattr(profile, field)
            if not value or value == '':
                missing.append({
                    'field': field,
                    'label': str(label),
                    'required': True
                })
        
        # فیلدهای اختیاری که پر نشده‌اند
        optional = {
            'tel': _('Telephone'),
            'avatar': _('Avatar'),
        }
        
        if profile.is_individual:
            optional['birth_date'] = _('Birth Date')
        
        for field, label in optional.items():
            value = getattr(profile, field)
            if not value or value == '':
                missing.append({
                    'field': field,
                    'label': str(label),
                    'required': False
                })
        
        return missing
    
    @classmethod
    @transaction.atomic
    def upload_avatar(cls, profile, avatar_file):
        """
        آپلود آواتار کاربر
        
        Args:
            profile: پروفایل کاربر
            avatar_file: فایل آپلود شده
        
        Returns:
            Profile: پروفایل به‌روزرسانی شده
        """
        # حذف آواتار قبلی
        if profile.avatar:
            profile.avatar.delete(save=False)
        
        # ذخیره آواتار جدید
        profile.avatar = avatar_file
        profile.save()
        
        logger.info(
            f"Avatar updated for user: {profile.user.email or profile.user.mobile}"
        )
        
        return profile
    
    @classmethod
    @transaction.atomic
    def remove_avatar(cls, profile):
        """
        حذف آواتار کاربر
        
        Args:
            profile: پروفایل کاربر
        
        Returns:
            Profile: پروفایل به‌روزرسانی شده
        """
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
        
        return profile
    
    @classmethod
    def get_profile_by_national_code(cls, national_code):
        """
        جستجوی پروفایل با کد ملی
        
        Args:
            national_code: کد ملی
        
        Returns:
            Profile or None
        """
        from apps.accounts.models import Profile
        return Profile.objects.filter(
            national_code=national_code,
            profile_type=ProfileType.INDIVIDUAL
        ).first()
    
    @classmethod
    def get_profile_by_national_id(cls, national_id):
        """
        جستجوی پروفایل با شناسه ملی
        
        Args:
            national_id: شناسه ملی
        
        Returns:
            Profile or None
        """
        from apps.accounts.models import Profile
        return Profile.objects.filter(
            national_id=national_id,
            profile_type=ProfileType.LEGAL
        ).first()
    
    @classmethod
    def get_profile_by_economic_code(cls, economic_code):
        """
        جستجوی پروفایل با کد اقتصادی
        
        Args:
            economic_code: کد اقتصادی
        
        Returns:
            Profile or None
        """
        from apps.accounts.models import Profile
        return Profile.objects.filter(
            economic_code=economic_code
        ).first()
    
    @classmethod
    def validate_profile_type_change(cls, profile, new_type):
        """
        بررسی امکان تغییر نوع پروفایل
        
        Args:
            profile: پروفایل کاربر
            new_type: نوع جدید
        
        Returns:
            dict: نتیجه اعتبارسنجی
        """
        result = {
            'can_change': True,
            'warnings': [],
            'requirements': [],
        }
        
        if profile.profile_type == new_type:
            result['can_change'] = False
            result['warnings'].append(_('Profile is already this type.'))
            return result
        
        # اگر حقیقی → حقوقی
        if new_type == ProfileType.LEGAL:
            result['requirements'] = [
                {
                    'field': 'company_name',
                    'label': _('Company Name'),
                    'type': 'string',
                    'max_length': 200
                },
                {
                    'field': 'national_id',
                    'label': _('National ID'),
                    'type': 'string',
                    'length': 11
                },
                {
                    'field': 'economic_code',
                    'label': _('Economic Code'),
                    'type': 'string',
                    'length': 12
                }
            ]
            
            # هشدار: اطلاعات حقیقی پاک می‌شود
            result['warnings'].append(
                _('Individual information (national code) will be cleared.')
            )
        
        # اگر حقوقی → حقیقی
        elif new_type == ProfileType.INDIVIDUAL:
            result['requirements'] = [
                {
                    'field': 'national_code',
                    'label': _('National Code'),
                    'type': 'string',
                    'length': 10
                }
            ]
            
            # هشدار: اطلاعات حقوقی پاک می‌شود
            result['warnings'].append(
                _('Legal information (company name, national ID, economic code) will be cleared.')
            )
        
        return result
    
    @classmethod
    def get_completion_suggestions(cls, profile):
        """
        دریافت پیشنهادات برای تکمیل پروفایل
        
        Args:
            profile: پروفایل کاربر
        
        Returns:
            list: لیست پیشنهادات
        """
        suggestions = []
        missing = cls.get_missing_fields(profile)
        
        if not missing:
            suggestions.append({
                'message': _('Your profile is complete!'),
                'type': 'success'
            })
            return suggestions
        
        # اولویت‌بندی پیشنهادات
        required_missing = [f for f in missing if f['required']]
        optional_missing = [f for f in missing if not f['required']]
        
        if required_missing:
            suggestions.append({
                'message': _('Complete required fields to unlock all features.'),
                'type': 'warning',
                'fields': [f['field'] for f in required_missing],
                'action': 'update_profile'
            })
        
        if optional_missing:
            suggestions.append({
                'message': _('Add optional information to improve your profile.'),
                'type': 'info',
                'fields': [f['field'] for f in optional_missing],
                'action': 'update_profile'
            })
        
        # پیشنهادات خاص
        if not profile.avatar:
            suggestions.append({
                'message': _('Add a profile picture to personalize your account.'),
                'type': 'tip',
                'action': 'upload_avatar'
            })
        
        return suggestions
    
    @classmethod
    def search_profiles(cls, query=None, profile_type=None, is_completed=None):
        """
        جستجوی پروفایل‌ها
        
        Args:
            query: عبارت جستجو
            profile_type: نوع پروفایل
            is_completed: فیلتر تکمیل بودن
        
        Returns:
            QuerySet
        """
        from apps.accounts.models import Profile
        from django.db.models import Q
        
        queryset = Profile.objects.all()
        
        if query:
            queryset = queryset.filter(
                Q(user__email__icontains=query) |
                Q(user__mobile__icontains=query) |
                Q(national_code__icontains=query) |
                Q(company_name__icontains=query) |
                Q(national_id__icontains=query) |
                Q(economic_code__icontains=query)
            )
        
        if profile_type:
            queryset = queryset.filter(profile_type=profile_type)
        
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed)
        
        return queryset.select_related('user')