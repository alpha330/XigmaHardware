from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    منیجر سفارشی برای مدیریت کاربران
    """

    def _create_user(self, email=None, mobile=None, password=None, **extra_fields):
        """
        ایجاد کاربر با ایمیل یا موبایل
        """
        if not email and not mobile:
            raise ValueError('Either email or mobile must be provided')

        # نرمال‌سازی ایمیل اگر وجود داشته باشد
        if email:
            email = self.normalize_email(email)

        user = self.model(
            email=email,
            mobile=mobile,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, mobile=None, password=None, **extra_fields):
        """ایجاد کاربر عادی"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, mobile, password, **extra_fields)

    def create_superuser(self, email=None, mobile=None, password=None, **extra_fields):
        """ایجاد سوپر ادمین"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'super_admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, mobile, password, **extra_fields)

    def create_by_email(self, email, password=None, **extra_fields):
        """ایجاد کاربر با ایمیل"""
        extra_fields['registration_method'] = 'email'
        return self._create_user(email=email, password=password, **extra_fields)

    def create_by_mobile(self, mobile, password=None, **extra_fields):
        """ایجاد کاربر با موبایل"""
        extra_fields['registration_method'] = 'mobile'
        return self._create_user(mobile=mobile, password=password, **extra_fields)

    def active(self):
        """کاربران فعال"""
        return self.filter(is_active=True)

    def verified(self):
        """کاربران تایید شده"""
        return self.active().filter(
            models.Q(is_email_verified=True) | models.Q(is_mobile_verified=True)
        )

    def by_role(self, role):
        """کاربران با نقش خاص"""
        return self.active().filter(role=role)