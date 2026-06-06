from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentGateway, PaymentLog
from django.utils.translation import gettext_lazy as _


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'type_badge', 'mode_badge',
        'is_default_badge', 'is_active', 'priority',
        'created_at_jalali',
    ]
    list_filter = ['gateway_type', 'mode', 'is_active', 'is_default']
    search_fields = ['name', 'api_key']

    fieldsets = (
        (_('Basic'), {
            'fields': ('name', 'gateway_type', 'mode', 'description')
        }),
        (_('API Credentials'), {
            'fields': ('api_key', 'sandbox_api_key', 'merchant_id')
        }),
        (_('Crypto (Optional)'), {
            'fields': ('wallet_address', 'network'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('callback_url', 'min_amount', 'max_amount', 'priority', 'extra_config')
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_default')
        }),
    )

    @admin.display(description=_('Type'))
    def type_badge(self, obj):
        colors = {
            'payping': '#17a2b8',
            'zarinpal': '#28a745',
            'crypto': '#ffc107',
            'card_to_card': '#6f42c1',
            'custom': '#6c757d',
        }
        color = colors.get(obj.gateway_type, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:4px; font-size:12px;">{}</span>',
            color, obj.get_gateway_type_display()
        )

    @admin.display(description=_('Mode'))
    def mode_badge(self, obj):
        color = '#ffc107' if obj.mode == 'test' else '#28a745'
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:4px; font-size:12px;">{}</span>',
            color, obj.get_mode_display()
        )

    @admin.display(description=_('Default'))
    def is_default_badge(self, obj):
        return '✅' if obj.is_default else '-'

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = [
        'id_short',  # ✅ تعریف شده پایین
        'user_info',
        'gateway_name',
        'amount_display',
        'status_badge',
        'gateway_code_short',
        'created_at_jalali',
    ]
    list_filter = ['status', 'gateway', 'created_at']
    search_fields = [
        'gateway_code', 'reference_code',
        'user__email', 'user__mobile',
    ]
    readonly_fields = [
        'id', 'user', 'gateway', 'amount',
        'gateway_code', 'reference_code',
        'gateway_request', 'gateway_response',
        'callback_data',
        'created_at', 'updated_at',
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Payment Info'), {
            'fields': ('id', 'user', 'gateway', 'amount', 'status')
        }),
        (_('References'), {
            'fields': ('gateway_code', 'reference_code', 'invoice', 'transaction')
        }),
        (_('Gateway Data'), {
            'fields': ('gateway_request', 'gateway_response', 'callback_data'),
            'classes': ('collapse',)
        }),
        (_('Details'), {
            'fields': ('description', 'payer_ip')
        }),
        (_('Timestamps'), {
            'fields': ('payment_date', 'verified_at', 'created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        return False

    # ==================== List Display Methods ====================

    @admin.display(description=_('ID'))
    def id_short(self, obj):  # ✅ تعریف شد
        return str(obj.id)[:8] + '...'

    @admin.display(description=_('User'))
    def user_info(self, obj):
        if obj.user:
            return format_html(
                '<b>{}</b><br/><small>{}</small>',
                obj.user.get_display_name(),
                obj.user.email or obj.user.mobile or ''
            )
        return '-'

    @admin.display(description=_('Gateway'))
    def gateway_name(self, obj):
        return obj.gateway.name if obj.gateway else '-'

    @admin.display(description=_('Amount'))
    def amount_display(self, obj):
        return format_html('<b>{:,}</b> Rials', int(obj.amount))

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {
            'pending': ('#ffc107', '⏳'),
            'redirected': ('#17a2b8', '🔀'),
            'verified': ('#28a745', '✅'),
            'failed': ('#dc3545', '❌'),
            'cancelled': ('#6c757d', '🚫'),
            'refunded': ('#6f42c1', '↩️'),
        }
        color, icon = colors.get(obj.status, ('#6c757d', '❓'))
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; '
            'border-radius:4px; font-size:11px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )

    @admin.display(description=_('Gateway Code'))
    def gateway_code_short(self, obj):
        if obj.gateway_code:
            return format_html('<code>{}</code>', obj.gateway_code[:15])
        return '-'

    @admin.display(description=_('Date'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')

    # ==================== Actions ====================

    actions = ['mark_as_verified', 'mark_as_failed']

    @admin.action(description=_('Mark selected as verified'))
    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        count = 0
        for log in queryset.filter(status__in=['pending', 'redirected']):
            log.status = 'verified'
            log.verified_at = timezone.now()
            log.reference_code = log.reference_code or f'ADMIN-{log.id}'
            log.save()
            count += 1
        self.message_user(request, _(f'{count} payment(s) verified.'))

    @admin.action(description=_('Mark selected as failed'))
    def mark_as_failed(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'redirected']).update(status='failed')
        self.message_user(request, _(f'{updated} payment(s) marked as failed.'), level='warning')