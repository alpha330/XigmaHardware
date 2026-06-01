import logging
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

logger = logging.getLogger(__name__)


class DeviceService:
    """
    سرویس مدیریت دستگاه‌های کاربر
    
    عملیات‌های اصلی:
    - ثبت دستگاه جدید
    - به‌روزرسانی اطلاعات دستگاه
    - مدیریت اعتماد به دستگاه‌ها
    - رهگیری فعالیت دستگاه‌ها
    - امنیت و تشخیص دستگاه‌های مشکوک
    """
    
    @classmethod
    def register_or_update_device(cls, user, request):
        """
        ثبت یا به‌روزرسانی دستگاه کاربر
        
        Args:
            user: کاربر
            request: request جاری
        
        Returns:
            UserDevice: دستگاه ثبت/به‌روزرسانی شده
        """
        from apps.accounts.models import UserDevice
        
        # دریافت اطلاعات از request
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = cls.get_client_ip(request)
        
        # Parse user agent
        device_info = cls.parse_user_agent(user_agent)
        
        # جستجوی دستگاه موجود
        device = UserDevice.objects.filter(
            user=user,
            user_agent=user_agent,
        ).first()
        
        if device:
            # به‌روزرسانی دستگاه موجود
            device.ip_address = ip_address
            device.last_used = timezone.now()
            device.is_active = True
            
            # به‌روزرسانی موقعیت جغرافیایی
            location = cls.get_geo_location(ip_address)
            if location:
                device.country = location.get('country', '')
                device.city = location.get('city', '')
            
            device.save()
            
            logger.debug(f"Device updated: {device.id} for user {user.email or user.mobile}")
        else:
            # ایجاد دستگاه جدید
            device = UserDevice.objects.create(
                user=user,
                device_name=device_info.get('device_name', 'Unknown Device'),
                device_type=device_info.get('device_type', 'Unknown'),
                operating_system=device_info.get('os', 'Unknown'),
                browser=device_info.get('browser', 'Unknown'),
                browser_version=device_info.get('browser_version', ''),
                ip_address=ip_address,
                user_agent=user_agent,
                country=device_info.get('country', ''),
                city=device_info.get('city', ''),
                is_active=True,
                is_trusted=False,
                last_used=timezone.now(),
            )
            
            logger.info(
                f"New device registered: {device.id} "
                f"for user {user.email or user.mobile}"
            )
        
        # ضمیمه کردن دستگاه به request
        request.device = device
        
        return device
    
    @classmethod
    def trust_device(cls, device):
        """
        اعتماد به یک دستگاه
        
        Args:
            device: دستگاه
        
        Returns:
            UserDevice: دستگاه به‌روزرسانی شده
        """
        device.is_trusted = True
        device.save(update_fields=['is_trusted'])
        
        logger.info(
            f"Device trusted: {device.id} "
            f"for user {device.user.email or device.user.mobile}"
        )
        
        return device
    
    @classmethod
    def revoke_device(cls, device):
        """
        لغو اعتماد و غیرفعال کردن دستگاه
        
        Args:
            device: دستگاه
        
        Returns:
            UserDevice: دستگاه به‌روزرسانی شده
        """
        device.is_active = False
        device.is_trusted = False
        device.save(update_fields=['is_active', 'is_trusted'])
        
        logger.info(
            f"Device revoked: {device.id} "
            f"for user {device.user.email or device.user.mobile}"
        )
        
        return device
    
    @classmethod
    def revoke_all_other_devices(cls, user, current_device):
        """
        لغو همه دستگاه‌ها به جز دستگاه جاری
        
        Args:
            user: کاربر
            current_device: دستگاه جاری
        
        Returns:
            int: تعداد دستگاه‌های لغو شده
        """
        count = user.devices.filter(is_active=True).exclude(
            id=current_device.id
        ).update(is_active=False, is_trusted=False)
        
        logger.info(
            f"Revoked {count} other devices for user {user.email or user.mobile}"
        )
        
        return count
    
    @classmethod
    def get_user_devices(cls, user, active_only=True):
        """
        دریافت دستگاه‌های کاربر
        
        Args:
            user: کاربر
            active_only: فقط دستگاه‌های فعال
        
        Returns:
            QuerySet
        """
        queryset = user.devices.all()
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-last_used')
    
    @classmethod
    def get_device_statistics(cls, user):
        """
        آمار دستگاه‌های کاربر
        
        Args:
            user: کاربر
        
        Returns:
            dict: آمار دستگاه‌ها
        """
        from apps.accounts.models import UserDevice
        
        devices = user.devices.all()
        
        return {
            'total_devices': devices.count(),
            'active_devices': devices.filter(is_active=True).count(),
            'trusted_devices': devices.filter(is_trusted=True).count(),
            'device_types': cls._count_by_field(devices, 'device_type'),
            'operating_systems': cls._count_by_field(devices, 'operating_system'),
            'browsers': cls._count_by_field(devices, 'browser'),
            'last_device_added': devices.order_by('-first_seen').first().first_seen if devices.exists() else None,
            'most_used_device': devices.order_by('-last_used').first().device_name if devices.exists() else None,
        }
    
    @classmethod
    def detect_suspicious_device(cls, user, request):
        """
        تشخیص دستگاه مشکوک
        
        Args:
            user: کاربر
            request: request جاری
        
        Returns:
            dict: نتیجه بررسی
        """
        ip_address = cls.get_client_ip(request)
        
        result = {
            'is_suspicious': False,
            'reasons': [],
            'risk_level': 'low',  # low, medium, high
        }
        
        # بررسی IP جدید
        known_ips = set(
            user.devices.filter(is_active=True).values_list('ip_address', flat=True)
        )
        
        if ip_address not in known_ips and known_ips:
            result['is_suspicious'] = True
            result['reasons'].append(_('Login from new IP address.'))
            result['risk_level'] = 'medium'
        
        # بررسی تغییر کشور
        device_info = cls.parse_user_agent(request.META.get('HTTP_USER_AGENT', ''))
        known_countries = set(
            user.devices.filter(
                is_active=True,
                country__isnull=False
            ).exclude(country='').values_list('country', flat=True)
        )
        
        if device_info.get('country') and known_countries:
            if device_info['country'] not in known_countries:
                result['is_suspicious'] = True
                result['reasons'].append(_('Login from new country.'))
                result['risk_level'] = 'high'
        
        # بررسی زمان غیرعادی
        from datetime import datetime
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            # اگر کاربر معمولاً در این ساعت فعال نیست
            usual_hours = cls._get_usual_active_hours(user)
            if usual_hours and current_hour not in usual_hours:
                result['is_suspicious'] = True
                result['reasons'].append(_('Login at unusual time.'))
                if result['risk_level'] != 'high':
                    result['risk_level'] = 'medium'
        
        if result['is_suspicious']:
            logger.warning(
                f"Suspicious device detected for user {user.email or user.mobile}: "
                f"{', '.join(result['reasons'])}"
            )
        
        return result
    
    @classmethod
    def cleanup_inactive_devices(cls, days=90):
        """
        پاکسازی دستگاه‌های غیرفعال قدیمی
        
        Args:
            days: تعداد روز
        
        Returns:
            int: تعداد دستگاه‌های پاکسازی شده
        """
        from django.utils import timezone
        from apps.accounts.models import UserDevice
        
        cutoff = timezone.now() - timezone.timedelta(days=days)
        
        count = UserDevice.objects.filter(
            is_active=False,
            last_used__lt=cutoff
        ).delete()[0]
        
        logger.info(f"Cleaned up {count} inactive devices older than {days} days")
        
        return count
    
    @classmethod
    def parse_user_agent(cls, user_agent_string):
        """
        Parse user agent string
        
        Args:
            user_agent_string: رشته user agent
        
        Returns:
            dict: اطلاعات دستگاه
        """
        device_info = {
            'device_name': 'Unknown Device',
            'device_type': 'Unknown',
            'os': 'Unknown',
            'browser': 'Unknown',
            'browser_version': '',
            'country': '',
            'city': '',
        }
        
        if not user_agent_string:
            return device_info
        
        # تشخیص نوع دستگاه
        if 'Mobile' in user_agent_string or 'Android' in user_agent_string:
            device_info['device_type'] = 'Mobile'
            if 'Android' in user_agent_string:
                device_info['os'] = 'Android'
        elif 'Tablet' in user_agent_string or 'iPad' in user_agent_string:
            device_info['device_type'] = 'Tablet'
            if 'iPad' in user_agent_string:
                device_info['os'] = 'iOS'
        else:
            device_info['device_type'] = 'Desktop'
        
        # تشخیص سیستم عامل
        if 'Windows NT 10' in user_agent_string:
            device_info['os'] = 'Windows 10'
        elif 'Windows NT 11' in user_agent_string:
            device_info['os'] = 'Windows 11'
        elif 'Windows' in user_agent_string:
            device_info['os'] = 'Windows'
        elif 'Mac OS X' in user_agent_string:
            device_info['os'] = 'macOS'
        elif 'Linux' in user_agent_string and 'Android' not in user_agent_string:
            device_info['os'] = 'Linux'
        elif 'iPhone' in user_agent_string:
            device_info['os'] = 'iOS'
            device_info['device_type'] = 'Mobile'
        
        # تشخیص مرورگر
        if 'Chrome' in user_agent_string and 'Edg' not in user_agent_string:
            device_info['browser'] = 'Chrome'
            # استخراج نسخه
            import re
            match = re.search(r'Chrome/(\d+)', user_agent_string)
            if match:
                device_info['browser_version'] = match.group(1)
        elif 'Firefox' in user_agent_string:
            device_info['browser'] = 'Firefox'
            import re
            match = re.search(r'Firefox/(\d+)', user_agent_string)
            if match:
                device_info['browser_version'] = match.group(1)
        elif 'Safari' in user_agent_string and 'Chrome' not in user_agent_string:
            device_info['browser'] = 'Safari'
            import re
            match = re.search(r'Version/(\d+)', user_agent_string)
            if match:
                device_info['browser_version'] = match.group(1)
        elif 'Edg' in user_agent_string:
            device_info['browser'] = 'Edge'
            import re
            match = re.search(r'Edg/(\d+)', user_agent_string)
            if match:
                device_info['browser_version'] = match.group(1)
        
        # ساخت نام دستگاه
        device_info['device_name'] = (
            f"{device_info['device_type']} - "
            f"{device_info['os']} - "
            f"{device_info['browser']}"
        )
        
        return device_info
    
    @classmethod
    def get_client_ip(cls, request):
        """
        دریافت IP کاربر از request
        
        Args:
            request: request جاری
        
        Returns:
            str: آدرس IP
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        return ip
    
    @classmethod
    def get_geo_location(cls, ip_address):
        """
        دریافت موقعیت جغرافیایی از IP
        
        توجه: در محیط واقعی از سرویس‌های GeoIP مثل MaxMind استفاده کنید
        
        Args:
            ip_address: آدرس IP
        
        Returns:
            dict: موقعیت جغرافیایی
        """
        # این یک پیاده‌سازی ساده است
        # در محیط واقعی از django-ipware و django-geoip2 استفاده کنید
        
        if ip_address in ['127.0.0.1', 'localhost', '0.0.0.0']:
            return {
                'country': 'Local',
                'city': 'Development',
            }
        
        # در اینجا می‌توانید از GeoIP استفاده کنید
        # from geoip2 import database
        # reader = database.Reader('/path/to/GeoLite2-City.mmdb')
        # response = reader.city(ip_address)
        # return {
        #     'country': response.country.name,
        #     'city': response.city.name,
        # }
        
        return None
    
    @classmethod
    def _count_by_field(cls, queryset, field):
        """
        شمارش تعداد بر اساس یک فیلد
        
        Args:
            queryset: QuerySet
            field: نام فیلد
        
        Returns:
            dict: نتیجه شمارش
        """
        from collections import Counter
        values = queryset.values_list(field, flat=True)
        return dict(Counter(values))
    
    @classmethod
    def _get_usual_active_hours(cls, user):
        """
        دریافت ساعات معمول فعالیت کاربر
        
        Args:
            user: کاربر
        
        Returns:
            set: ساعات فعالیت
        """
        # این تابع نیاز به ذخیره history فعالیت دارد
        # می‌توانید یک مدل ActivityLog ایجاد کنید
        return set()
    
    @classmethod
    def notify_suspicious_login(cls, user, device_info):
        """
        ارسال نوتیفیکیشن برای ورود مشکوک
        
        Args:
            user: کاربر
            device_info: اطلاعات دستگاه
        """
        from apps.accounts.tasks import send_security_notification
        
        send_security_notification.delay(
            user_id=str(user.id),
            subject=_('Suspicious Login Detected'),
            message=_(
                f'We detected a login from a new device:\n'
                f'Device: {device_info.get("device_name")}\n'
                f'IP: {device_info.get("ip_address")}\n'
                f'Location: {device_info.get("city")}, {device_info.get("country")}\n\n'
                f'If this was you, you can ignore this message.\n'
                f'If not, please change your password immediately.'
            )
        )


# برای استفاده در جاهای دیگر
device_service = DeviceService()