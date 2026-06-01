import logging
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthService:
    """
    سرویس مدیریت احراز هویت
    """
    
    signer = TimestampSigner()
    
    @classmethod
    def register_by_email(cls, email, password, **extra_fields):
        """
        ثبت‌نام با ایمیل
        """
        if User.objects.filter(email=email).exists():
            raise ValueError(_('This email is already registered.'))
        
        user = User.objects.create_by_email(
            email=email,
            password=password,
            **extra_fields
        )
        
        return user
    
    @classmethod
    def register_by_mobile(cls, mobile, password=None, **extra_fields):
        """
        ثبت‌نام با موبایل
        """
        if User.objects.filter(mobile=mobile).exists():
            raise ValueError(_('This mobile is already registered.'))
        
        # اگر رمز عبور داده نشده، رمز تصادفی تولید کن
        if not password:
            import secrets
            password = secrets.token_urlsafe(16)
        
        user = User.objects.create_by_mobile(
            mobile=mobile,
            password=password,
            **extra_fields
        )
        
        return user
    
    @classmethod
    def authenticate_user(cls, email=None, mobile=None, password=None, otp_code=None):
        """
        احراز هویت کاربر با ایمیل/موبایل و رمز عبور یا OTP
        """
        user = None
        
        # پیدا کردن کاربر
        if email:
            user = User.objects.filter(email=email).first()
        elif mobile:
            user = User.objects.filter(mobile=mobile).first()
        
        if not user:
            return None
        
        # بررسی قفل بودن حساب
        if user.is_locked:
            return None
        
        # احراز هویت با OTP
        if otp_code:
            from apps.accounts.models import OTPCode
            otp = OTPCode.objects.filter(
                user=user,
                code=otp_code,
                purpose='login',
                is_used=False
            ).first()
            
            if otp and otp.is_valid():
                otp.verify(otp_code)
                user.reset_failed_login()
                return user
            else:
                user.increment_failed_login()
                return None
        
        # احراز هویت با رمز عبور
        if password:
            # استفاده از authenticate استاندارد
            if email:
                auth_user = authenticate(email=email, password=password)
            else:
                auth_user = authenticate(mobile=mobile, password=password)
            
            if auth_user:
                user.reset_failed_login()
                return auth_user
            else:
                user.increment_failed_login()
                return None
        
        return None
    
    @classmethod
    def update_login_info(cls, user, request):
        """
        به‌روزرسانی اطلاعات ورود
        """
        user.last_login = timezone.now()
        user.last_activity = timezone.now()
        user.last_login_ip = cls.get_client_ip(request)
        
        # تشخیص روش ورود
        if request.data.get('email'):
            user.last_login_method = 'email'
        elif request.data.get('mobile'):
            user.last_login_method = 'mobile'
        
        user.save()
    
    @classmethod
    def register_device(cls, user, request):
        """
        ثبت دستگاه کاربر
        """
        from apps.accounts.models import UserDevice
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = cls.get_client_ip(request)
        
        # Parse user agent (در محیط واقعی از کتابخانه user-agents استفاده کن)
        device_info = cls.parse_user_agent(user_agent)
        
        # ایجاد یا به‌روزرسانی دستگاه
        device, created = UserDevice.objects.update_or_create(
            user=user,
            user_agent=user_agent,
            defaults={
                'ip_address': ip_address,
                'device_type': device_info.get('device_type', 'Unknown'),
                'operating_system': device_info.get('os', 'Unknown'),
                'browser': device_info.get('browser', 'Unknown'),
                'browser_version': device_info.get('browser_version', ''),
                'is_active': True,
                'last_used': timezone.now(),
            }
        )
        
        # ضمیمه کردن دستگاه به request
        request.device = device
        
        return device
    
    @classmethod
    def verify_email_token(cls, token):
        """
        تایید توکن ایمیل
        """
        try:
            user_id = cls.signer.unsign(token, max_age=86400)  # 24 ساعت
            return User.objects.get(id=user_id)
        except (BadSignature, SignatureExpired, User.DoesNotExist):
            return None
    
    @classmethod
    def generate_email_token(cls, user):
        """
        تولید توکن تایید ایمیل
        """
        return cls.signer.sign(str(user.id))
    
    @classmethod
    def find_user_by_email_or_mobile(cls, value):
        """
        پیدا کردن کاربر با ایمیل یا موبایل
        """
        if '@' in value:
            return User.objects.filter(email=value).first()
        else:
            return User.objects.filter(mobile=value).first()
    
    @classmethod
    def revoke_all_tokens(cls, user):
        """
        باطل کردن همه توکن‌های کاربر
        """
        try:
            from rest_framework_simplejwt.tokens import OutstandingToken
            OutstandingToken.objects.filter(user=user).delete()
        except Exception as e:
            logger.error(f"Revoke tokens failed: {str(e)}")
    
    @staticmethod
    def get_client_ip(request):
        """
        دریافت IP کاربر از request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def parse_user_agent(user_agent_string):
        """
        Parse user agent string (نسخه ساده)
        در محیط واقعی از کتابخانه user-agents استفاده کن
        """
        device_info = {
            'device_type': 'Unknown',
            'os': 'Unknown',
            'browser': 'Unknown',
            'browser_version': '',
        }
        
        if not user_agent_string:
            return device_info
        
        # تشخیص موبایل
        if 'Mobile' in user_agent_string or 'Android' in user_agent_string:
            device_info['device_type'] = 'Mobile'
        elif 'Tablet' in user_agent_string or 'iPad' in user_agent_string:
            device_info['device_type'] = 'Tablet'
        else:
            device_info['device_type'] = 'Desktop'
        
        # تشخیص سیستم عامل
        if 'Windows' in user_agent_string:
            device_info['os'] = 'Windows'
        elif 'Mac' in user_agent_string:
            device_info['os'] = 'macOS'
        elif 'Linux' in user_agent_string:
            device_info['os'] = 'Linux'
        elif 'Android' in user_agent_string:
            device_info['os'] = 'Android'
        elif 'iOS' in user_agent_string or 'iPhone' in user_agent_string:
            device_info['os'] = 'iOS'
        
        # تشخیص مرورگر
        if 'Chrome' in user_agent_string:
            device_info['browser'] = 'Chrome'
        elif 'Firefox' in user_agent_string:
            device_info['browser'] = 'Firefox'
        elif 'Safari' in user_agent_string:
            device_info['browser'] = 'Safari'
        elif 'Edge' in user_agent_string:
            device_info['browser'] = 'Edge'
        
        return device_info