import logging
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class UserService:
    """
    سرویس مدیریت کاربران
    
    عملیات‌های اصلی:
    - ایجاد کاربر
    - به‌روزرسانی کاربر
    - حذف (غیرفعال‌سازی) کاربر
    - مدیریت نقش‌ها
    - مدیریت وضعیت تایید
    - جستجو و فیلتر کاربران
    """
    
    @classmethod
    @transaction.atomic
    def create_user(cls, email=None, mobile=None, password=None, **extra_fields):
        """
        ایجاد کاربر جدید با ایمیل یا موبایل
        
        Args:
            email: ایمیل کاربر (اختیاری)
            mobile: شماره موبایل (اختیاری)
            password: رمز عبور
            **extra_fields: فیلدهای اضافی
        
        Returns:
            User: کاربر ایجاد شده
        
        Raises:
            ValueError: اگر ایمیل و موبایل هر دو خالی باشند
        """
        if not email and not mobile:
            raise ValueError(_('Either email or mobile must be provided.'))
        
        # تنظیم روش ثبت‌نام
        if email and mobile:
            extra_fields['registration_method'] = 'email'  # اولویت با ایمیل
        elif email:
            extra_fields['registration_method'] = 'email'
        else:
            extra_fields['registration_method'] = 'mobile'
        
        # تنظیم نام‌های پیش‌فرض
        if 'first_name' not in extra_fields:
            extra_fields['first_name'] = ''
        if 'last_name' not in extra_fields:
            extra_fields['last_name'] = ''
        
        # ایجاد کاربر
        user = User.objects.create_user(
            email=email,
            mobile=mobile,
            password=password,
            **extra_fields
        )
        
        logger.info(
            f"User created: {user.email or user.mobile} "
            f"role: {user.role}"
        )
        
        return user
    
    @classmethod
    @transaction.atomic
    def update_user(cls, user, data):
        """
        به‌روزرسانی اطلاعات کاربر
        
        Args:
            user: نمونه کاربر
            data: دیکشنری داده‌های جدید
        
        Returns:
            User: کاربر به‌روزرسانی شده
        """
        # فیلدهای مجاز برای به‌روزرسانی توسط خود کاربر
        allowed_fields = ['first_name', 'last_name']
        
        # اگر ادمین است، فیلدهای بیشتری می‌تواند تغییر دهد
        if user.is_superuser or user.is_staff:
            allowed_fields.extend(['email', 'mobile', 'role', 'is_active'])
        
        # اعمال تغییرات
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # اگر ایمیل تغییر کرده، وضعیت تایید را ریست کن
        if 'email' in data and data['email'] != user.email:
            user.is_email_verified = False
            # ارسال ایمیل تایید جدید
            from apps.accounts.tasks import send_verification_email
            send_verification_email.delay(str(user.id))
        
        # اگر موبایل تغییر کرده، وضعیت تایید را ریست کن
        if 'mobile' in data and data['mobile'] != user.mobile:
            user.is_mobile_verified = False
        
        user.save()
        
        logger.info(f"User updated: {user.email or user.mobile}")
        
        return user
    
    @classmethod
    @transaction.atomic
    def deactivate_user(cls, user, reason=''):
        """
        غیرفعال‌سازی کاربر (Soft Delete)
        
        Args:
            user: کاربر مورد نظر
            reason: دلیل غیرفعال‌سازی
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        user.is_active = False
        user.save()
        
        # ثبت دلیل در پروفایل (اگر فیلد exists)
        if hasattr(user, 'profile') and hasattr(user.profile, 'deactivation_reason'):
            user.profile.deactivation_reason = reason
            user.profile.save()
        
        # باطل کردن توکن‌ها
        from apps.accounts.services.auth_service import AuthService
        AuthService.revoke_all_tokens(user)
        
        logger.info(
            f"User deactivated: {user.email or user.mobile} "
            f"reason: {reason}"
        )
        
        return True
    
    @classmethod
    @transaction.atomic
    def activate_user(cls, user):
        """
        فعال‌سازی مجدد کاربر
        
        Args:
            user: کاربر مورد نظر
        
        Returns:
            bool: موفقیت‌آمیز بودن عملیات
        """
        user.is_active = True
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        
        logger.info(f"User activated: {user.email or user.mobile}")
        
        return True
    
    @classmethod
    @transaction.atomic
    def change_role(cls, user, new_role):
        """
        تغییر نقش کاربر
        
        Args:
            user: کاربر مورد نظر
            new_role: نقش جدید
        
        Returns:
            User: کاربر به‌روزرسانی شده
        
        Raises:
            ValueError: اگر نقش نامعتبر باشد
        """
        from apps.accounts.enums import UserRole
        
        # بررسی معتبر بودن نقش
        valid_roles = [choice[0] for choice in UserRole.choices]
        if new_role not in valid_roles:
            raise ValueError(_(f'Invalid role: {new_role}'))
        
        old_role = user.role
        user.role = new_role
        
        # تنظیم is_staff برای نقش‌های مدیریتی
        if new_role in ['super_admin', 'admin']:
            user.is_staff = True
        elif old_role in ['super_admin', 'admin']:
            # اگر از نقش مدیریتی خارج می‌شود
            # فقط سوپر ادمین می‌تواند is_staff را تغییر دهد
            pass
        
        user.save()
        
        logger.info(
            f"User role changed: {user.email or user.mobile} "
            f"from {old_role} to {new_role}"
        )
        
        return user
    
    @classmethod
    def verify_user_email(cls, user):
        """
        تایید ایمیل کاربر
        
        Args:
            user: کاربر مورد نظر
        """
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified', 'updated_at'])
        
        logger.info(f"Email verified for user: {user.email}")
        
        return user
    
    @classmethod
    def verify_user_mobile(cls, user):
        """
        تایید موبایل کاربر
        
        Args:
            user: کاربر مورد نظر
        """
        user.is_mobile_verified = True
        user.save(update_fields=['is_mobile_verified', 'updated_at'])
        
        logger.info(f"Mobile verified for user: {user.mobile}")
        
        return user
    
    @classmethod
    def get_user_by_identifier(cls, identifier):
        """
        پیدا کردن کاربر با ایمیل یا موبایل
        
        Args:
            identifier: ایمیل یا شماره موبایل
        
        Returns:
            User or None
        """
        if '@' in identifier:
            return User.objects.filter(email=identifier).first()
        else:
            return User.objects.filter(mobile=identifier).first()
    
    @classmethod
    def get_user_by_id(cls, user_id):
        """
        دریافت کاربر با ID
        
        Args:
            user_id: شناسه کاربر
        
        Returns:
            User or None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @classmethod
    def search_users(cls, query=None, role=None, is_active=None, 
                     is_verified=None, ordering='-created_at'):
        """
        جستجو و فیلتر کاربران
        
        Args:
            query: عبارت جستجو (ایمیل، موبایل، نام)
            role: فیلتر نقش
            is_active: فیلتر فعال/غیرفعال
            is_verified: فیلتر تایید شده
            ordering: مرتب‌سازی
        
        Returns:
            QuerySet
        """
        from django.db.models import Q
        
        queryset = User.objects.all()
        
        # جستجوی متنی
        if query:
            queryset = queryset.filter(
                Q(email__icontains=query) |
                Q(mobile__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(profile__company_name__icontains=query)
            )
        
        # فیلتر نقش
        if role:
            queryset = queryset.filter(role=role)
        
        # فیلتر وضعیت فعال
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        # فیلتر وضعیت تایید
        if is_verified is not None:
            if is_verified:
                queryset = queryset.filter(
                    Q(is_email_verified=True) | Q(is_mobile_verified=True)
                )
            else:
                queryset = queryset.filter(
                    is_email_verified=False,
                    is_mobile_verified=False
                )
        
        return queryset.order_by(ordering)
    
    @classmethod
    def get_user_statistics(cls, user):
        """
        دریافت آمار کاربر
        
        Args:
            user: کاربر
        
        Returns:
            dict: آمار کاربر
        """
        stats = {
            'total_orders': 0,
            'total_payments': 0,
            'total_transactions': 0,
            'wallet_balance': 0,
            'devices_count': 0,
            'profile_completion': 0,
        }
        
        # تعداد سفارشات (اگر اپ market وجود دارد)
        if hasattr(user, 'orders'):
            stats['total_orders'] = user.orders.count()
        
        # تراکنش‌های کیف پول
        if hasattr(user, 'wallet'):
            stats['wallet_balance'] = float(user.wallet.balance)
            stats['total_transactions'] = user.wallet.transactions.count()
        
        # دستگاه‌ها
        if hasattr(user, 'devices'):
            stats['devices_count'] = user.devices.filter(is_active=True).count()
        
        # تکمیل پروفایل
        if hasattr(user, 'profile'):
            stats['profile_completion'] = cls._calculate_profile_completion(user.profile)
        
        return stats
    
    @classmethod
    def _calculate_profile_completion(cls, profile):
        """
        محاسبه درصد تکمیل پروفایل
        
        Args:
            profile: پروفایل کاربر
        
        Returns:
            int: درصد تکمیل (0-100)
        """
        if profile.is_individual:
            fields = [
                'national_code', 'address', 'postal_code',
                'tel', 'avatar', 'birth_date'
            ]
        else:
            fields = [
                'company_name', 'national_id', 'economic_code',
                'address', 'postal_code', 'tel'
            ]
        
        filled = sum(1 for field in fields if getattr(profile, field))
        percentage = int((filled / len(fields)) * 100)
        
        return percentage
    
    @classmethod
    def get_users_by_role(cls, role):
        """
        دریافت کاربران با نقش خاص
        
        Args:
            role: نقش مورد نظر
        
        Returns:
            QuerySet
        """
        return User.objects.filter(role=role, is_active=True)
    
    @classmethod
    def get_new_users(cls, days=7):
        """
        دریافت کاربران جدید در n روز گذشته
        
        Args:
            days: تعداد روز
        
        Returns:
            QuerySet
        """
        from django.utils import timezone
        since = timezone.now() - timezone.timedelta(days=days)
        return User.objects.filter(created_at__gte=since)
    
    @classmethod
    def get_active_users(cls):
        """
        دریافت کاربران فعال (آنلاین در 30 دقیقه اخیر)
        
        Returns:
            QuerySet
        """
        from django.utils import timezone
        thirty_min_ago = timezone.now() - timezone.timedelta(minutes=30)
        return User.objects.filter(
            is_active=True,
            last_activity__gte=thirty_min_ago
        )
    
    @classmethod
    def check_user_exists(cls, email=None, mobile=None):
        """
        بررسی وجود کاربر با ایمیل یا موبایل
        
        Args:
            email: ایمیل (اختیاری)
            mobile: موبایل (اختیاری)
        
        Returns:
            dict: نتیجه بررسی
        """
        result = {
            'exists': False,
            'email_exists': False,
            'mobile_exists': False,
        }
        
        if email:
            result['email_exists'] = User.objects.filter(email=email).exists()
        
        if mobile:
            result['mobile_exists'] = User.objects.filter(mobile=mobile).exists()
        
        result['exists'] = result['email_exists'] or result['mobile_exists']
        
        return result
    
    @classmethod
    def bulk_activate_users(cls, user_ids):
        """
        فعال‌سازی گروهی کاربران
        
        Args:
            user_ids: لیست شناسه‌های کاربران
        
        Returns:
            int: تعداد کاربران فعال شده
        """
        count = User.objects.filter(
            id__in=user_ids,
            is_active=False
        ).update(is_active=True)
        
        logger.info(f"Bulk activated {count} users")
        
        return count
    
    @classmethod
    def bulk_deactivate_users(cls, user_ids, reason=''):
        """
        غیرفعال‌سازی گروهی کاربران
        
        Args:
            user_ids: لیست شناسه‌های کاربران
            reason: دلیل غیرفعال‌سازی
        
        Returns:
            int: تعداد کاربران غیرفعال شده
        """
        count = User.objects.filter(
            id__in=user_ids,
            is_active=True
        ).update(is_active=False)
        
        logger.info(f"Bulk deactivated {count} users, reason: {reason}")
        
        return count
    
    @classmethod
    @transaction.atomic
    def merge_users(cls, primary_user_id, secondary_user_id):
        """
        ادغام دو کاربر (انتقال همه اطلاعات به کاربر اصلی)
        
        Args:
            primary_user_id: شناسه کاربر اصلی
            secondary_user_id: شناسه کاربر ثانویه
        
        Returns:
            User: کاربر اصلی پس از ادغام
        """
        try:
            primary = User.objects.get(id=primary_user_id)
            secondary = User.objects.get(id=secondary_user_id)
        except User.DoesNotExist:
            raise ValueError(_('User not found'))
        
        # انتقال کیف پول
        if hasattr(secondary, 'wallet') and hasattr(primary, 'wallet'):
            # انتقال موجودی
            primary.wallet.balance += secondary.wallet.balance
            primary.wallet.save()
            
            # انتقال تراکنش‌ها
            secondary.wallet.transactions.update(wallet=primary.wallet)
        
        # انتقال سایر اطلاعات (در اپ‌های دیگر)
        # این بخش بستگی به مدل‌های دیگر دارد
        
        # غیرفعال‌سازی کاربر ثانویه
        secondary.is_active = False
        secondary.save()
        
        logger.info(
            f"Users merged: {secondary.email or secondary.mobile} -> "
            f"{primary.email or primary.mobile}"
        )
        
        return primary
    
    @classmethod
    def get_user_growth_stats(cls, days=30):
        """
        آمار رشد کاربران
        
        Args:
            days: تعداد روز
        
        Returns:
            dict: آمار رشد
        """
        from django.utils import timezone
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        
        since = timezone.now() - timezone.timedelta(days=days)
        
        daily_stats = User.objects.filter(
            created_at__gte=since
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return {
            'total_new_users': User.objects.filter(created_at__gte=since).count(),
            'daily_breakdown': list(daily_stats),
            'total_active': User.objects.filter(is_active=True).count(),
            'total_verified': User.objects.filter(
                is_email_verified=True
            ).count() + User.objects.filter(
                is_mobile_verified=True
            ).count(),
        }