"""
Celery Tasks for Accounts App

شامل تسک‌های:
- ارسال ایمیل (خوش‌آمدگویی، تایید، بازیابی رمز)
- ارسال SMS/OTP
- پردازش‌های دوره‌ای (پاکسازی OTP، غیرفعال‌سازی کاربران)
- اعلان‌های امنیتی
- گزارش‌گیری
"""

import logging
from datetime import timedelta
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()
logger = get_task_logger(__name__)


# ============================================================
# Email Tasks
# ============================================================

@shared_task(
    name='accounts.send_welcome_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    rate_limit='10/m'
)
def send_welcome_email(self, user_id):
    """
    ارسال ایمیل خوش‌آمدگویی به کاربر جدید
    
    Args:
        user_id: شناسه کاربر
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            logger.warning(f"User {user_id} has no email, skipping welcome email")
            return
        
        # آماده‌سازی context
        context = {
            'user': user,
            'site_name': getattr(settings, 'SITE_NAME', 'Marketplace'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@marketplace.com'),
            'current_year': timezone.now().year,
        }
        
        # رندر قالب HTML
        html_content = render_to_string('accounts/emails/welcome.html', context)
        text_content = render_to_string('accounts/emails/welcome.txt', context)
        
        # ارسال ایمیل
        subject = _('Welcome to {site_name}!').format(site_name=context['site_name'])
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Welcome email sent to {user.email}")
        
        return f"Welcome email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send welcome email to user {user_id}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='accounts.send_verification_email',
    bind=True,
    max_retries=3,
    default_retry_delay=120
)
def send_verification_email(self, user_id):
    """
    ارسال ایمیل تایید حساب کاربری
    
    Args:
        user_id: شناسه کاربر
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            logger.warning(f"User {user_id} has no email")
            return
        
        # تولید توکن تایید
        from apps.accounts.services.auth_service import AuthService
        token = AuthService.generate_email_token(user)
        
        # لینک تایید
        verification_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/api/accounts/auth/verify/email/{token}/"
        
        context = {
            'user': user,
            'verification_url': verification_url,
            'token': token,
            'site_name': getattr(settings, 'SITE_NAME', 'Marketplace'),
            'expiry_hours': 24,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@marketplace.com'),
        }
        
        # رندر قالب
        html_content = render_to_string('accounts/emails/verify_email.html', context)
        text_content = render_to_string('accounts/emails/verify_email.txt', context)
        
        # ارسال
        subject = _('Verify your email address')
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Verification email sent to {user.email}")
        
        return f"Verification email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send verification email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='accounts.send_password_reset_email',
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_password_reset_email(self, user_id):
    """
    ارسال ایمیل بازیابی رمز عبور
    
    Args:
        user_id: شناسه کاربر
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            logger.warning(f"User {user_id} has no email")
            return
        
        # تولید توکن
        from apps.accounts.services.auth_service import AuthService
        token = AuthService.generate_email_token(user)
        
        # لینک بازیابی
        reset_url = f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/auth/reset-password/?token={token}&email={user.email}"
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'token': token,
            'site_name': getattr(settings, 'SITE_NAME', 'Marketplace'),
            'expiry_minutes': 30,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@marketplace.com'),
            'ip_address': user.last_login_ip or 'Unknown',
        }
        
        html_content = render_to_string('accounts/emails/reset_password.html', context)
        text_content = render_to_string('accounts/emails/reset_password.txt', context)
        
        subject = _('Reset Your Password')
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Password reset email sent to {user.email}")
        
        return f"Password reset email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send password reset email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='accounts.send_security_notification',
    bind=True,
    max_retries=2,
    default_retry_delay=30
)
def send_security_notification(self, user_id, subject, message):
    """
    ارسال ایمیل اعلان امنیتی
    
    Args:
        user_id: شناسه کاربر
        subject: موضوع ایمیل
        message: متن پیام
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.email:
            logger.warning(f"User {user_id} has no email")
            return
        
        context = {
            'user': user,
            'message': message,
            'site_name': getattr(settings, 'SITE_NAME', 'Marketplace'),
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@marketplace.com'),
            'timestamp': timezone.now(),
        }
        
        html_content = render_to_string('accounts/emails/security_alert.html', context)
        text_content = render_to_string('accounts/emails/security_alert.txt', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Security notification sent to {user.email}: {subject}")
        
        return f"Security notification sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send security notification: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='accounts.send_email_bulk',
    bind=True,
    max_retries=2,
    default_retry_delay=300
)
def send_email_bulk(self, user_ids, subject, template_name, context=None):
    """
    ارسال ایمیل گروهی به کاربران
    
    Args:
        user_ids: لیست شناسه‌های کاربران
        subject: موضوع ایمیل
        template_name: نام قالب
        context: context اضافی
    """
    try:
        users = User.objects.filter(id__in=user_ids, is_active=True)
        
        if context is None:
            context = {}
        
        success_count = 0
        fail_count = 0
        
        for user in users:
            if not user.email:
                continue
            
            try:
                user_context = {
                    **context,
                    'user': user,
                    'site_name': getattr(settings, 'SITE_NAME', 'Marketplace'),
                    'current_year': timezone.now().year,
                }
                
                html_content = render_to_string(f'accounts/emails/{template_name}.html', user_context)
                text_content = render_to_string(f'accounts/emails/{template_name}.txt', user_context)
                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {str(e)}")
                fail_count += 1
        
        logger.info(f"Bulk email sent: {success_count} success, {fail_count} failed")
        
        return f"Bulk email: {success_count} sent, {fail_count} failed"
        
    except Exception as exc:
        logger.error(f"Bulk email task failed: {str(exc)}")
        raise self.retry(exc=exc)


# ============================================================
# SMS/OTP Tasks
# ============================================================

@shared_task(
    name='accounts.send_otp_sms',
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    rate_limit='20/m'
)
def send_otp_sms(self, user_id, otp_code):
    """
    ارسال کد OTP از طریق SMS
    
    توجه: در محیط واقعی باید از سرویس SMS مثل کاوه‌نگار استفاده کنید
    
    Args:
        user_id: شناسه کاربر
        otp_code: کد OTP
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.mobile:
            logger.warning(f"User {user_id} has no mobile")
            return
        
        # اینجا باید با سرویس SMS ادغام کنید
        # مثال با کاوه‌نگار:
        # from kavenegar import KavenegarAPI
        # api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        # params = {
        #     'sender': settings.SMS_SENDER_NUMBER,
        #     'receptor': user.mobile,
        #     'message': f'کد تایید شما: {otp_code}\nMarketplace',
        # }
        # response = api.sms_send(params)
        
        # در محیط توسعه فقط لاگ می‌کنیم
        logger.info(f"[DEV] OTP for {user.mobile}: {otp_code}")
        
        # شبیه‌سازی ارسال موفق
        return f"OTP sent to {user.mobile}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send OTP SMS: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='accounts.send_sms_notification',
    bind=True,
    max_retries=2,
    default_retry_delay=30
)
def send_sms_notification(self, user_id, message):
    """
    ارسال پیامک اطلاع‌رسانی
    
    Args:
        user_id: شناسه کاربر
        message: متن پیام
    """
    try:
        user = User.objects.get(id=user_id)
        
        if not user.mobile:
            logger.warning(f"User {user_id} has no mobile")
            return
        
        # ادغام با سرویس SMS
        logger.info(f"[DEV] SMS notification to {user.mobile}: {message}")
        
        return f"SMS sent to {user.mobile}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to send SMS: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='accounts.send_otp_sms_bulk',
    bind=True,
    max_retries=1
)
def send_otp_sms_bulk(self, mobile_numbers, message):
    """
    ارسال پیامک گروهی
    
    Args:
        mobile_numbers: لیست شماره‌های موبایل
        message: متن پیام
    """
    try:
        # در محیط واقعی با سرویس SMS ادغام کنید
        success_count = 0
        
        for mobile in mobile_numbers:
            try:
                # ارسال SMS
                logger.info(f"[DEV] Bulk SMS to {mobile}: {message}")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send SMS to {mobile}: {str(e)}")
        
        return f"Bulk SMS: {success_count} sent out of {len(mobile_numbers)}"
        
    except Exception as exc:
        logger.error(f"Bulk SMS task failed: {str(exc)}")
        raise self.retry(exc=exc)


# ============================================================
# Scheduled Tasks (Periodic)
# ============================================================

@shared_task(
    name='accounts.clean_expired_otps'
)
def clean_expired_otps():
    """
    پاکسازی کدهای OTP منقضی شده
    
    اجرا: هر یک ساعت
    """
    try:
        from apps.accounts.models import OTPCode
        
        # حذف OTPهای منقضی شده یا استفاده شده
        expired = OTPCode.objects.filter(
            expires_at__lt=timezone.now()
        )
        
        used_old = OTPCode.objects.filter(
            is_used=True,
            used_at__lt=timezone.now() - timedelta(hours=24)
        )
        
        total_count = expired.count() + used_old.count()
        
        expired.delete()
        used_old.delete()
        
        logger.info(f"Cleaned {total_count} expired/used OTP codes")
        
        return f"Cleaned {total_count} OTP codes"
        
    except Exception as e:
        logger.error(f"Failed to clean OTP codes: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(
    name='accounts.deactivate_inactive_users'
)
def deactivate_inactive_users():
    """
    غیرفعال‌سازی کاربران غیرفعال طولانی مدت
    
    اجرا: هر روز ساعت 2 صبح
    """
    try:
        # کاربرانی که بیش از 6 ماه فعالیت نداشته‌اند
        inactive_threshold = timezone.now() - timedelta(days=180)
        
        inactive_users = User.objects.filter(
            is_active=True,
            last_activity__lt=inactive_threshold
        )
        
        count = inactive_users.count()
        
        if count > 0:
            # ارسال ایمیل هشدار قبل از غیرفعال‌سازی
            for user in inactive_users[:100]:  # محدودیت برای جلوگیری از overload
                send_security_notification.delay(
                    user_id=str(user.id),
                    subject=_('Account Inactivity Warning'),
                    message=_(
                        'Your account has been inactive for more than 6 months. '
                        'It will be deactivated in 7 days if no activity is detected.'
                    )
                )
            
            # غیرفعال‌سازی کاربرانی که بیش از 7 ماه غیرفعال هستند
            deactivation_threshold = timezone.now() - timedelta(days=210)
            users_to_deactivate = inactive_users.filter(
                last_activity__lt=deactivation_threshold
            )
            
            deactivated_count = users_to_deactivate.update(
                is_active=False
            )
            
            logger.info(
                f"Deactivated {deactivated_count} inactive users, "
                f"warned {min(count, 100)} users"
            )
            
            return f"Deactivated {deactivated_count} users, warned {min(count, 100)}"
        
        return "No inactive users to process"
        
    except Exception as e:
        logger.error(f"Failed to deactivate inactive users: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(
    name='accounts.unlock_locked_accounts'
)
def unlock_locked_accounts():
    """
    باز کردن قفل حساب‌های کاربری که زمان قفلشان گذشته
    
    اجرا: هر 30 دقیقه
    """
    try:
        # کاربرانی که زمان قفلشان تمام شده
        unlocked_users = User.objects.filter(
            locked_until__isnull=False,
            locked_until__lt=timezone.now()
        )
        
        count = unlocked_users.count()
        
        unlocked_users.update(
            locked_until=None,
            failed_login_attempts=0
        )
        
        if count > 0:
            logger.info(f"Unlocked {count} user accounts")
        
        return f"Unlocked {count} accounts"
        
    except Exception as e:
        logger.error(f"Failed to unlock accounts: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(
    name='accounts.clean_old_devices'
)
def clean_old_devices():
    """
    پاکسازی دستگاه‌های قدیمی و غیرفعال
    
    اجرا: هر هفته
    """
    try:
        from apps.accounts.services.device_service import DeviceService
        
        # پاکسازی دستگاه‌های غیرفعال قدیمی (بیش از 90 روز)
        count = DeviceService.cleanup_inactive_devices(days=90)
        
        logger.info(f"Cleaned {count} old inactive devices")
        
        return f"Cleaned {count} devices"
        
    except Exception as e:
        logger.error(f"Failed to clean devices: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(
    name='accounts.generate_user_report'
)
def generate_user_report(report_type='daily'):
    """
    تولید گزارش کاربران
    
    Args:
        report_type: نوع گزارش (daily, weekly, monthly)
    """
    try:
        from apps.accounts.services.user_service import UserService
        
        # تعیین بازه زمانی
        if report_type == 'daily':
            days = 1
        elif report_type == 'weekly':
            days = 7
        elif report_type == 'monthly':
            days = 30
        else:
            days = 1
        
        # دریافت آمار
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'new_users': UserService.get_new_users(days=days).count(),
            'verified_users': User.objects.filter(
                is_email_verified=True
            ).count() + User.objects.filter(
                is_mobile_verified=True
            ).count(),
            'growth_stats': UserService.get_user_growth_stats(days=days),
            'report_type': report_type,
            'generated_at': timezone.now().isoformat(),
        }
        
        logger.info(f"Generated {report_type} user report: {stats['new_users']} new users")
        
        # ذخیره گزارش در دیتابیس یا ارسال به ادمین
        # می‌توانید یک مدل Report ایجاد کنید
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        return f"Error: {str(e)}"


# ============================================================
# Monitoring & Health Tasks
# ============================================================

@shared_task(
    name='accounts.check_system_health'
)
def check_system_health():
    """
    بررسی سلامت سیستم
    
    اجرا: هر 5 دقیقه
    """
    try:
        health_status = {
            'database': False,
            'redis': False,
            'celery_workers': False,
            'email_service': False,
            'sms_service': False,
            'timestamp': timezone.now().isoformat(),
        }
        
        # بررسی دیتابیس
        try:
            User.objects.first()
            health_status['database'] = True
        except Exception:
            pass
        
        # بررسی Redis
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['redis'] = True
        except Exception:
            pass
        
        # بررسی Celery Workers
        try:
            from celery import current_app
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            if stats:
                health_status['celery_workers'] = True
        except Exception:
            pass
        
        # لاگ کردن وضعیت
        unhealthy = [k for k, v in health_status.items() if not v and k != 'timestamp']
        
        if unhealthy:
            logger.warning(f"System health issues detected: {', '.join(unhealthy)}")
        else:
            logger.info("System health check passed")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {'error': str(e)}


@shared_task(
    name='accounts.send_admin_daily_report'
)
def send_admin_daily_report():
    """
    ارسال گزارش روزانه به ادمین
    
    اجرا: هر روز ساعت 8 صبح
    """
    try:
        from apps.accounts.services.user_service import UserService
        
        # آمار 24 ساعت گذشته
        yesterday = timezone.now() - timedelta(days=1)
        
        stats = {
            'new_users': User.objects.filter(created_at__gte=yesterday).count(),
            'total_users': User.objects.count(),
            'active_users_today': User.objects.filter(
                last_activity__gte=yesterday
            ).count(),
            'unverified_users': User.objects.filter(
                is_email_verified=False,
                is_mobile_verified=False
            ).count(),
        }
        
        # ارسال ایمیل به ادمین
        admin_emails = User.objects.filter(
            is_superuser=True,
            is_active=True,
            email__isnull=False
        ).values_list('email', flat=True)
        
        if admin_emails:
            context = {
                'stats': stats,
                'date': timezone.now().strftime('%Y-%m-%d'),
                'site_name': getattr(settings, 'SITE_NAME', 'Marketplace'),
            }
            
            html_content = render_to_string('accounts/emails/admin_daily_report.html', context)
            text_content = render_to_string('accounts/emails/admin_daily_report.txt', context)
            
            subject = _('Daily Report - {date}').format(date=context['date'])
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=list(admin_emails),
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            logger.info(f"Daily report sent to {len(admin_emails)} admins")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to send daily report: {str(e)}")
        return f"Error: {str(e)}"


# ============================================================
# Wallet Related Tasks
# ============================================================

@shared_task(
    name='accounts.process_wallet_transaction',
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def process_wallet_transaction(self, transaction_id):
    """
    پردازش تراکنش کیف پول
    
    Args:
        transaction_id: شناسه تراکنش
    """
    try:
        from apps.accounts.models import WalletTransaction
        from apps.accounts.services.wallet_service import WalletService
        
        transaction = WalletTransaction.objects.get(id=transaction_id)
        
        if transaction.status != 'pending':
            return f"Transaction {transaction_id} is not pending"
        
        # پردازش بر اساس نوع تراکنش
        if transaction.transaction_type == 'deposit':
            # تایید واریز (درگاه پرداخت)
            transaction.complete()
            
        elif transaction.transaction_type == 'withdraw':
            # بررسی و تایید برداشت
            if transaction.wallet.available_balance >= transaction.amount:
                transaction.wallet.withdraw(transaction.amount)
                transaction.complete()
            else:
                transaction.fail('Insufficient balance')
        
        logger.info(f"Transaction {transaction_id} processed: {transaction.status}")
        
        return f"Transaction {transaction_id}: {transaction.status}"
        
    except WalletTransaction.DoesNotExist:
        logger.error(f"Transaction {transaction_id} not found")
        return f"Transaction {transaction_id} not found"
        
    except Exception as exc:
        logger.error(f"Failed to process transaction {transaction_id}: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(
    name='accounts.sync_wallet_balance'
)
def sync_wallet_balance(wallet_id):
    """
    همگام‌سازی موجودی کیف پول با تراکنش‌ها
    
    Args:
        wallet_id: شناسه کیف پول
    """
    try:
        from apps.accounts.models import Wallet, WalletTransaction
        from django.db.models import Sum
        
        wallet = Wallet.objects.get(id=wallet_id)
        
        # محاسبه مجموع تراکنش‌ها
        completed_transactions = wallet.transactions.filter(status='completed')
        
        total_deposits = completed_transactions.filter(
            transaction_type='deposit'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_withdrawals = completed_transactions.filter(
            transaction_type='withdraw'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # به‌روزرسانی موجودی
        calculated_balance = total_deposits - total_withdrawals
        
        if wallet.balance != calculated_balance:
            old_balance = wallet.balance
            wallet.balance = calculated_balance
            wallet.save(update_fields=['balance'])
            
            logger.info(
                f"Wallet {wallet_id} balance synced: "
                f"{old_balance} -> {calculated_balance}"
            )
        
        return f"Wallet {wallet_id} balance: {wallet.balance}"
        
    except Wallet.DoesNotExist:
        logger.error(f"Wallet {wallet_id} not found")
        return f"Wallet {wallet_id} not found"
        
    except Exception as e:
        logger.error(f"Failed to sync wallet {wallet_id}: {str(e)}")
        return f"Error: {str(e)}"


# ============================================================
# Utility Tasks
# ============================================================

@shared_task(
    name='accounts.export_users_csv'
)
def export_users_csv(admin_email=None):
    """
    خروجی CSV کاربران برای ادمین
    
    Args:
        admin_email: ایمیل ادمین برای ارسال فایل
    """
    try:
        import csv
        import io
        from django.core.mail import EmailMessage
        
        # تولید CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # هدر
        writer.writerow([
            'ID', 'Email', 'Mobile', 'First Name', 'Last Name',
            'Role', 'Is Active', 'Is Email Verified', 'Is Mobile Verified',
            'Registration Method', 'Date Joined', 'Last Login'
        ])
        
        # داده‌ها
        users = User.objects.all().select_related('profile')
        
        for user in users.iterator(chunk_size=1000):
            writer.writerow([
                str(user.id),
                user.email or '',
                user.mobile or '',
                user.first_name,
                user.last_name,
                user.role,
                user.is_active,
                user.is_email_verified,
                user.is_mobile_verified,
                user.registration_method,
                user.created_at.isoformat(),
                user.last_login.isoformat() if user.last_login else '',
            ])
        
        # ذخیره یا ارسال
        csv_content = output.getvalue()
        output.close()
        
        if admin_email:
            # ارسال ایمیل
            email = EmailMessage(
                subject=_('Users Export'),
                body=_('Attached is the users export CSV file.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
            )
            email.attach('users_export.csv', csv_content, 'text/csv')
            email.send()
            
            logger.info(f"Users CSV exported and sent to {admin_email}")
        
        return f"Exported {users.count()} users"
        
    except Exception as e:
        logger.error(f"Failed to export users: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(
    name='accounts.backup_user_data'
)
def backup_user_data(user_id):
    """
    تهیه backup از داده‌های کاربر قبل از حذف
    
    Args:
        user_id: شناسه کاربر
    """
    try:
        import json
        from django.core.serializers import serialize
        
        user = User.objects.get(id=user_id)
        
        backup_data = {
            'user': json.loads(serialize('json', [user]))[0],
            'backup_date': timezone.now().isoformat(),
        }
        
        # اضافه کردن پروفایل
        if hasattr(user, 'profile'):
            backup_data['profile'] = json.loads(
                serialize('json', [user.profile])
            )[0]
        
        # اضافه کردن کیف پول
        if hasattr(user, 'wallet'):
            backup_data['wallet'] = json.loads(
                serialize('json', [user.wallet])
            )[0]
            backup_data['transactions'] = json.loads(
                serialize('json', user.wallet.transactions.all())
            )
        
        # ذخیره در فایل یا دیتابیس
        # می‌توانید یک مدل UserBackup ایجاد کنید
        backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
        
        # در محیط واقعی در S3 یا similar ذخیره کنید
        logger.info(f"Backup created for user {user_id}")
        
        return f"Backup created for user {user_id}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return f"User {user_id} not found"
        
    except Exception as e:
        logger.error(f"Failed to backup user {user_id}: {str(e)}")
        return f"Error: {str(e)}"