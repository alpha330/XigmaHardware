from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, Profile, Wallet, WalletTransaction, UserDevice, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    پنل مدیریت کاربران با قابلیت‌های پیشرفته
    """
    
    # لیست نمایش
    list_display = [
        'id', 'display_name_with_avatar', 'email', 'mobile',
        'role_badge', 'verification_status', 'wallet_balance',
        'is_active', 'last_login_persian', 'created_at_persian'
    ]
    
    list_display_links = ['id', 'display_name_with_avatar']
    
    # فیلترها
    list_filter = [
        'role',
        'is_active',
        'is_email_verified',
        'is_mobile_verified',
        'registration_method',
        'created_at',
        'last_login',
    ]
    
    # جستجو
    search_fields = [
        'email',
        'mobile',
        'id',
        'profile__first_name',
        'profile__last_name',
        'profile__company_name',
        'profile__national_code',
    ]
    
    # مرتب‌سازی پیش‌فرض
    ordering = ['-created_at']
    
    # فیلدهای فقط خواندنی
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'last_login',
        'last_login_ip', 'last_activity'
    ]
    
    # صفحه‌بندی
    list_per_page = 50
    
    # اکشن‌های دسته‌جمعی
    actions = [
        'activate_users',
        'deactivate_users',
        'verify_email',
        'verify_mobile',
        'reset_failed_login',
    ]
    
    # گروه‌بندی فیلدها در فرم ویرایش
    fieldsets = (
        (_('Authentication Information'), {
            'fields': ('email', 'mobile', 'password')
        }),
        (_('Personal Information'), {
            'fields': ('registration_method', 'role')
        }),
        (_('Verification Status'), {
            'fields': ('is_email_verified', 'is_mobile_verified')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Security Information'), {
            'fields': (
                'last_login_ip', 'last_login_method',
                'failed_login_attempts', 'locked_until'
            ),
            'classes': ('collapse',)
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'last_activity', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # فیلدهای فرم ایجاد کاربر جدید
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'mobile', 'password1', 'password2',
                'role', 'is_staff', 'is_superuser'
            ),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """
        سفارشی‌سازی فرم بر اساس نوع عملیات
        """
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # ایجاد کاربر جدید
            form.base_fields['email'].required = False
            form.base_fields['mobile'].required = False
        return form
    
    def save_model(self, request, obj, form, change):
        """
        ذخیره مدل با تنظیم روش ثبت‌نام
        """
        if not change:  # کاربر جدید
            if obj.email and not obj.mobile:
                obj.registration_method = 'email'
            elif obj.mobile and not obj.email:
                obj.registration_method = 'mobile'
            elif obj.email and obj.mobile:
                obj.registration_method = 'email'  # اولویت با ایمیل
        
        super().save_model(request, obj, form, change)
    
    # === Custom Display Methods ===
    
    @admin.display(description=_('User'))
    def display_name_with_avatar(self, obj):
        """نمایش نام کاربر با آواتار"""
        avatar_html = ''
        if hasattr(obj, 'profile') and obj.profile.avatar:
            avatar_html = format_html(
                '<img src="{}" style="width: 30px; height: 30px; '
                'border-radius: 50%; margin-right: 8px; vertical-align: middle;" />',
                obj.profile.avatar.url
            )
        
        name = obj.get_display_name()
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '{} <span>{}</span>'
            '</div>',
            avatar_html, name
        )
    
    @admin.display(description=_('Role'))
    def role_badge(self, obj):
        """نمایش نقش با رنگ"""
        role_colors = {
            'super_admin': ('#dc3545', 'Super Admin'),
            'client': ('#28a745', 'Client'),
            'accountant': ('#17a2b8', 'Accountant'),
            'courier': ('#ffc107', 'Courier'),
            'stock_keeper': ('#6f42c1', 'Stock Keeper'),
        }
        
        color, label = role_colors.get(obj.role, ('#6c757d', obj.role))
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 8px; border-radius: 4px; font-size: 12px;">'
            '{}</span>',
            color, label
        )
    
    @admin.display(description=_('Verification'))
    def verification_status(self, obj):
        """نمایش وضعیت تایید"""
        if obj.is_email_verified and obj.is_mobile_verified:
            icon, color, text = '✓✓', '#28a745', 'Full'
        elif obj.is_email_verified:
            icon, color, text = '✓', '#17a2b8', 'Email'
        elif obj.is_mobile_verified:
            icon, color, text = '✓', '#17a2b8', 'Mobile'
        else:
            icon, color, text = '✗', '#dc3545', 'None'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span> '
            '<span style="font-size: 12px;">({})</span>',
            color, icon, text
        )
    
    @admin.display(description=_('Balance'))
    def wallet_balance(self, obj):
        """نمایش موجودی کیف پول"""
        if hasattr(obj, 'wallet'):
            balance = obj.wallet.balance
            color = '#28a745' if balance > 0 else '#6c757d'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:,.0f}</span> '
                '<span style="font-size: 11px;">Rials</span>',
                color, balance
            )
        return format_html(
            '<span style="color: #dc3545;">No Wallet</span>'
        )
    
    @admin.display(description=_('Last Login'))
    def last_login_persian(self, obj):
        """نمایش آخرین ورود به فارسی"""
        if obj.last_login:
            from django.utils import timezone
            import jdatetime
            jalali_date = jdatetime.datetime.fromgregorian(
                datetime=obj.last_login
            )
            return jalali_date.strftime('%Y/%m/%d %H:%M')
        return '-'
    
    @admin.display(description=_('Created'))
    def created_at_persian(self, obj):
        """نمایش تاریخ ایجاد به فارسی"""
        import jdatetime
        jalali_date = jdatetime.datetime.fromgregorian(
            datetime=obj.created_at
        )
        return jalali_date.strftime('%Y/%m/%d')
    
    # === Admin Actions ===
    
    @admin.action(description=_('Activate selected users'))
    def activate_users(self, request, queryset):
        """فعال‌سازی کاربران انتخاب شده"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _(f'{updated} user(s) activated successfully.')
        )
    
    @admin.action(description=_('Deactivate selected users'))
    def deactivate_users(self, request, queryset):
        """غیرفعال‌سازی کاربران انتخاب شده"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            _(f'{updated} user(s) deactivated successfully.'),
            level='warning'
        )
    
    @admin.action(description=_('Verify email for selected users'))
    def verify_email(self, request, queryset):
        """تایید ایمیل کاربران انتخاب شده"""
        updated = queryset.update(is_email_verified=True)
        self.message_user(
            request,
            _(f'{updated} user(s) email verified.')
        )
    
    @admin.action(description=_('Verify mobile for selected users'))
    def verify_mobile(self, request, queryset):
        """تایید موبایل کاربران انتخاب شده"""
        updated = queryset.update(is_mobile_verified=True)
        self.message_user(
            request,
            _(f'{updated} user(s) mobile verified.')
        )
    
    @admin.action(description=_('Reset failed login attempts'))
    def reset_failed_login(self, request, queryset):
        """بازنشانی تلاش‌های ناموفق ورود"""
        updated = queryset.update(
            failed_login_attempts=0,
            locked_until=None
        )
        self.message_user(
            request,
            _(f'{updated} user(s) failed login attempts reset.')
        )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    پنل مدیریت پروفایل‌ها
    """
    
    list_display = [
        'user_email', 'user_mobile', 'profile_type_badge',
        'full_name_or_company', 'national_code_or_id',
        'is_completed', 'updated_at_persian'
    ]
    
    list_filter = [
        'profile_type',
        'is_completed',
        'created_at',
    ]
    
    search_fields = [
        'user__email',
        'user__mobile',
        'national_code',
        'company_name',
        'national_id',
        'economic_code',
    ]
    
    readonly_fields = [
        'id', 'user', 'created_at', 'updated_at'
    ]
    
    list_per_page = 50
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'profile_type')
        }),
        (_('Individual Fields'), {
            'fields': ('national_code',),
            'classes': ('collapse',)
        }),
        (_('Legal/Company Fields'), {
            'fields': ('company_name', 'national_id', 'economic_code'),
            'classes': ('collapse',)
        }),
        (_('Contact Information'), {
            'fields': ('tel', 'address', 'postal_code')
        }),
        (_('Additional'), {
            'fields': ('avatar', 'birth_date', 'is_completed')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('Email')
    user_email.admin_order_field = 'user__email'
    
    def user_mobile(self, obj):
        return obj.user.mobile
    user_mobile.short_description = _('Mobile')
    user_mobile.admin_order_field = 'user__mobile'
    
    @admin.display(description=_('Profile Type'))
    def profile_type_badge(self, obj):
        """نمایش نوع پروفایل با رنگ"""
        if obj.is_individual:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; '
                'padding: 2px 8px; border-radius: 12px;">'
                '👤 Individual</span>'
            )
        return format_html(
            '<span style="background-color: #6f42c1; color: white; '
            'padding: 2px 8px; border-radius: 12px;">'
            '🏢 Legal</span>'
        )
    
    @admin.display(description=_('Name/Company'))
    def full_name_or_company(self, obj):
        """نمایش نام شخص یا شرکت"""
        if obj.is_individual:
            return obj.full_name or '-'
        return obj.company_name or '-'
    
    @admin.display(description=_('National Code/ID'))
    def national_code_or_id(self, obj):
        """نمایش کد ملی یا شناسه ملی"""
        if obj.is_individual:
            return obj.national_code or '-'
        return obj.national_id or '-'
    
    @admin.display(description=_('Updated'))
    def updated_at_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.updated_at
        ).strftime('%Y/%m/%d %H:%M')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    پنل مدیریت کیف پول‌ها
    """
    
    list_display = [
        'user_display', 'balance_display',
        'blocked_balance_display', 'available_balance_display',
        'total_transactions', 'is_active_status',
        'updated_at_persian'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
    ]
    
    search_fields = [
        'user__email',
        'user__mobile',
        'id',
    ]
    
    readonly_fields = [
        'id', 'user', 'balance', 'blocked_balance',
        'created_at', 'updated_at'
    ]
    
    list_per_page = 50
    
    def user_display(self, obj):
        return obj.user.get_display_name()
    user_display.short_description = _('User')
    user_display.admin_order_field = 'user__email'
    
    @admin.display(description=_('Balance'))
    def balance_display(self, obj):
        return format_html(
            '<span style="font-weight: bold;">{:,.0f}</span> Rials',
            obj.balance
        )
    
    @admin.display(description=_('Blocked'))
    def blocked_balance_display(self, obj):
        if obj.blocked_balance > 0:
            return format_html(
                '<span style="color: #ffc107;">{:,.0f}</span> Rials',
                obj.blocked_balance
            )
        return '0 Rials'
    
    @admin.display(description=_('Available'))
    def available_balance_display(self, obj):
        available = obj.available_balance
        color = '#28a745' if available > 0 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:,.0f}</span> Rials',
            color, available
        )
    
    @admin.display(description=_('Transactions'))
    def total_transactions(self, obj):
        count = obj.transactions.count()
        return format_html(
            '<a href="{}?wallet__id__exact={}">{} transactions</a>',
            '/admin/accounts/wallettransaction/', obj.id, count
        )
    
    @admin.display(description=_('Status'))
    def is_active_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: #28a745;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Inactive</span>'
        )
    
    def updated_at_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.updated_at
        ).strftime('%Y/%m/%d %H:%M')
    updated_at_persian.short_description = _('Updated')


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    """
    پنل مدیریت تراکنش‌های کیف پول
    """
    
    list_display = [
        'id', 'wallet_user', 'transaction_type_badge',
        'amount_display', 'status_badge',
        'balance_change', 'reference_id',
        'created_at_persian'
    ]
    
    list_filter = [
        'transaction_type',
        'status',
        'created_at',
    ]
    
    search_fields = [
        'wallet__user__email',
        'wallet__user__mobile',
        'reference_id',
        'id',
        'description',
    ]
    
    readonly_fields = [
        'id', 'wallet', 'transaction_type',
        'amount', 'balance_before', 'balance_after',
        'completed_at', 'created_at'
    ]
    
    list_per_page = 100
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Transaction Info'), {
            'fields': (
                'wallet', 'transaction_type', 'amount',
                'status', 'reference_id'
            )
        }),
        (_('Balance Details'), {
            'fields': ('balance_before', 'balance_after')
        }),
        (_('Additional Info'), {
            'fields': ('description', 'metadata'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def wallet_user(self, obj):
        return obj.wallet.user.get_display_name()
    wallet_user.short_description = _('User')
    wallet_user.admin_order_field = 'wallet__user__email'
    
    @admin.display(description=_('Type'))
    def transaction_type_badge(self, obj):
        type_colors = {
            'deposit': '#28a745',
            'withdraw': '#dc3545',
            'payment': '#ffc107',
            'refund': '#17a2b8',
            'commission': '#6f42c1',
            'bonus': '#fd7e14',
        }
        color = type_colors.get(obj.transaction_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 4px; font-size: 11px;">'
            '{}</span>',
            color, obj.get_transaction_type_display()
        )
    
    @admin.display(description=_('Amount'))
    def amount_display(self, obj):
        color = '#28a745' if obj.transaction_type == 'deposit' else '#dc3545'
        prefix = '+' if obj.transaction_type in ['deposit', 'refund', 'bonus'] else '-'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {:,.0f}</span> Rials',
            color, prefix, obj.amount
        )
    
    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        status_colors = {
            'pending': '#ffc107',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 4px; font-size: 11px;">'
            '{}</span>',
            color, obj.get_status_display()
        )
    
    @admin.display(description=_('Balance Change'))
    def balance_change(self, obj):
        if obj.balance_before is not None and obj.balance_after is not None:
            return format_html(
                '<span style="font-size: 11px;">'
                '{:,.0f} → {:,.0f}'
                '</span>',
                obj.balance_before, obj.balance_after
            )
        return '-'
    
    @admin.display(description=_('Created'))
    def created_at_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.created_at
        ).strftime('%Y/%m/%d %H:%M')
    
    def has_add_permission(self, request):
        """جلوگیری از ایجاد دستی تراکنش"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """فقط خواندنی برای تراکنش‌های تکمیل شده"""
        if obj and obj.status != 'pending':
            return False
        return super().has_change_permission(request, obj)


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    """
    پنل مدیریت دستگاه‌های کاربران
    """
    
    list_display = [
        'user_display', 'device_info',
        'ip_address', 'location',
        'trusted_badge', 'last_used_persian'
    ]
    
    list_filter = [
        'device_type',
        'is_active',
        'is_trusted',
        'last_used',
    ]
    
    search_fields = [
        'user__email',
        'user__mobile',
        'ip_address',
        'device_name',
    ]
    
    readonly_fields = [
        'id', 'user', 'device_name', 'device_type',
        'operating_system', 'browser', 'browser_version',
        'ip_address', 'user_agent', 'country', 'city',
        'first_seen', 'last_used', 'created_at'
    ]
    
    list_per_page = 50
    
    actions = ['trust_devices', 'revoke_trust']
    
    def user_display(self, obj):
        return obj.user.get_display_name()
    user_display.short_description = _('User')
    
    @admin.display(description=_('Device Info'))
    def device_info(self, obj):
        info_parts = []
        if obj.device_type:
            info_parts.append(obj.device_type)
        if obj.operating_system:
            info_parts.append(obj.operating_system)
        if obj.browser:
            info_parts.append(f"{obj.browser} {obj.browser_version or ''}")
        return ' | '.join(info_parts) if info_parts else '-'
    
    @admin.display(description=_('Location'))
    def location(self, obj):
        if obj.city and obj.country:
            return f"{obj.city}, {obj.country}"
        elif obj.country:
            return obj.country
        return '-'
    
    @admin.display(description=_('Trusted'))
    def trusted_badge(self, obj):
        if obj.is_trusted:
            return format_html(
                '<span style="color: #28a745;">✓ Trusted</span>'
            )
        return format_html(
            '<span style="color: #6c757d;">✗ Not Trusted</span>'
        )
    
    @admin.display(description=_('Last Used'))
    def last_used_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.last_used
        ).strftime('%Y/%m/%d %H:%M')
    
    @admin.action(description=_('Trust selected devices'))
    def trust_devices(self, request, queryset):
        updated = queryset.update(is_trusted=True)
        self.message_user(
            request,
            _(f'{updated} device(s) trusted.')
        )
    
    @admin.action(description=_('Revoke trust from selected devices'))
    def revoke_trust(self, request, queryset):
        updated = queryset.update(is_trusted=False)
        self.message_user(
            request,
            _(f'{updated} device(s) untrusted.'),
            level='warning'
        )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    """
    پنل مدیریت کدهای OTP
    """
    
    list_display = [
        'user_display', 'code_masked',
        'purpose', 'sent_via',
        'is_valid_status', 'attempts',
        'created_at_persian'
    ]
    
    list_filter = [
        'purpose',
        'sent_via',
        'is_used',
        'created_at',
    ]
    
    search_fields = [
        'user__email',
        'user__mobile',
        'code',
    ]
    
    readonly_fields = [
        'id', 'user', 'code', 'purpose',
        'sent_via', 'is_used', 'attempts',
        'expires_at', 'used_at', 'created_at'
    ]
    
    list_per_page = 100
    
    def user_display(self, obj):
        return obj.user.get_display_name()
    user_display.short_description = _('User')
    
    @admin.display(description=_('Code'))
    def code_masked(self, obj):
        """نمایش کد به صورت ماسک شده"""
        if obj.is_used:
            return format_html(
                '<span style="color: #6c757d;">●●●●●●</span>'
            )
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            obj.code
        )
    
    @admin.display(description=_('Valid'))
    def is_valid_status(self, obj):
        if obj.is_valid():
            return format_html(
                '<span style="color: #28a745;">✓ Valid</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Invalid</span>'
        )
    
    @admin.display(description=_('Created'))
    def created_at_persian(self, obj):
        import jdatetime
        return jdatetime.datetime.fromgregorian(
            datetime=obj.created_at
        ).strftime('%Y/%m/%d %H:%M')
    
    def has_add_permission(self, request):
        """جلوگیری از ایجاد دستی OTP"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """فقط خواندنی"""
        return False