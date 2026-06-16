from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Invoice, InvoiceItem, FinancialTransaction, FinancialReport,Coupon
from .enums import InvoiceType, InvoiceStatus, PaymentMethod, PaymentStatus

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']
    list_filter = ['discount_type', 'is_active']

# ============================================================
# Inline Models
# ============================================================

class InvoiceItemInline(admin.TabularInline):
    """اقلام فاکتور داخل Invoice"""
    model = InvoiceItem
    extra = 0
    fields = [
        'product', 'description', 'sku',
        'quantity', 'unit_price_display', 'discount_percent',
        'total_price_display',
    ]
    readonly_fields = ['unit_price_display', 'total_price_display']
    can_delete = True
    show_change_link = False

    def unit_price_display(self, obj):
        return format_html('<b>{:,}</b>', int(obj.unit_price))
    unit_price_display.short_description = _('Unit Price')

    def total_price_display(self, obj):
        return format_html(
            '<span style="color: #e94560; font-weight: bold;">{:,}</span>',
            int(obj.total_price)
        )
    total_price_display.short_description = _('Total')


class PaymentInline(admin.TabularInline):
    """پرداخت‌های فاکتور"""
    model = FinancialTransaction
    fk_name = 'invoice'
    extra = 0
    fields = [
        'transaction_number', 'amount_display', 'status_badge',
        'payment_method_badge', 'transaction_date_jalali', 'reference_code',
    ]
    readonly_fields = [
        'transaction_number', 'amount_display', 'status_badge',
        'payment_method_badge', 'transaction_date_jalali', 'reference_code',
    ]
    can_delete = False
    max_num = 0
    ordering = ['-transaction_date']

    def amount_display(self, obj):
        color = '#28a745' if obj.transaction_type in ['deposit', 'refund', 'wallet_charge'] else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:,}</span>',
            color, int(obj.amount)
        )
    amount_display.short_description = _('Amount')

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'verified': '#28a745',
            'failed': '#dc3545',
            'refunded': '#17a2b8',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'), obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    def payment_method_badge(self, obj):
        if obj.payment_method:
            return obj.get_payment_method_display()
        return '-'
    payment_method_badge.short_description = _('Method')

    def transaction_date_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.transaction_date
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.transaction_date.strftime('%Y-%m-%d %H:%M')
    transaction_date_jalali.short_description = _('Date')


# ============================================================
# Invoice Admin
# ============================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number_short', 'user_info', 'type_badge',
        'status_badge', 'items_count_display', 'amount_summary',
        'payment_progress', 'payment_due_date_jalali',
        'created_at_jalali',
    ]
    list_filter = [
        'invoice_type', 'status', 'payment_method',
        'created_at', 'payment_due_date',
    ]
    search_fields = [
        'invoice_number', 'user__email', 'user__mobile',
        'user__first_name', 'user__last_name',
        'billing_company', 'billing_national_id',
        'items__description',
    ]
    readonly_fields = [
        'id', 'invoice_number', 'subtotal', 'tax_amount',
        'total_amount', 'paid_amount', 'remaining_amount',
        'created_at', 'updated_at', 'paid_at',
    ]
    autocomplete_fields = ['user', 'cart', 'related_invoice', 'created_by', 'approved_by']

    fieldsets = (
        (_('Invoice Information'), {
            'fields': ('id', 'invoice_number', 'invoice_type', 'status')
        }),
        (_('Customer'), {
            'fields': ('user', 'cart', 'related_invoice')
        }),
        (_('Pricing'), {
            'fields': (
                'subtotal', 'discount_amount', 'tax_amount',
                'shipping_amount', 'total_amount',
                'paid_amount', 'remaining_amount', 'currency'
            )
        }),
        (_('Payment'), {
            'fields': ('payment_method', 'payment_due_date', 'paid_at')
        }),
        (_('Billing Information'), {
            'fields': (
                'billing_name', 'billing_company',
                'billing_national_id', 'billing_economic_code',
                'billing_address', 'billing_postal_code', 'billing_phone'
            ),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('notes', 'customer_notes')
        }),
        (_('Approval'), {
            'fields': ('created_by', 'approved_by', 'approved_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [InvoiceItemInline, PaymentInline]
    list_per_page = 50
    date_hierarchy = 'created_at'

    # ==================== List Display Methods ====================

    @admin.display(description=_('Invoice #'))
    def invoice_number_short(self, obj):
        return format_html('<code style="font-size:11px;">{}</code>', obj.invoice_number[:20])

    @admin.display(description=_('User'), ordering='user__email')
    def user_info(self, obj):
        if obj.user:
            return format_html(
                '<div><b>{}</b></div><small style="color:#666;">{}</small>',
                obj.user.get_display_name(),
                obj.user.email or obj.user.mobile or ''
            )
        return '-'

    @admin.display(description=_('Type'))
    def type_badge(self, obj):
        colors = {
            'proforma': ('#17a2b8', '📄'),
            'final': ('#28a745', '✅'),
            'wallet_charge': ('#ffc107', '💰'),
            'refund': ('#dc3545', '↩️'),
        }
        color, icon = colors.get(obj.invoice_type, ('#6c757d', '📄'))
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{} {}</span>',
            color, icon, obj.get_invoice_type_display()
        )

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {
            'draft': ('#6c757d', '📝'),
            'pending': ('#ffc107', '⏳'),
            'paid': ('#28a745', '✅'),
            'partially_paid': ('#17a2b8', '💳'),
            'cancelled': ('#dc3545', '❌'),
            'expired': ('#343a40', '⏰'),
            'refunded': ('#6f42c1', '↩️'),
        }
        color, icon = colors.get(obj.status, ('#6c757d', '❓'))
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 8px; '
            'border-radius:4px; font-size:11px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )

    @admin.display(description=_('Items'))
    def items_count_display(self, obj):
        return obj.items_count

    @admin.display(description=_('Amount'))
    def amount_summary(self, obj):
        total = int(obj.total_amount)
        paid = int(obj.paid_amount)

        html = f'<b>{total:,}</b> Rials'

        if obj.discount_amount > 0:
            html += f'<br/><small style="color:#e94560;">Disc: {int(obj.discount_amount):,}</small>'

        if obj.tax_amount > 0:
            html += f'<br/><small style="color:#6c757d;">Tax: {int(obj.tax_amount):,}</small>'

        return format_html(html)

    @admin.display(description=_('Payment'))
    def payment_progress(self, obj):
        if obj.is_fully_paid:
            return format_html('<span style="color:#28a745;">✅ Paid</span>')

        total = int(obj.total_amount)
        paid = int(obj.paid_amount)

        if total == 0:
            percent = 0
        else:
            percent = int(paid / total * 100)

        return format_html(
            '<div style="background:#e9ecef; border-radius:10px; height:18px; width:120px;">'
            '<div style="background:linear-gradient(90deg, #28a745, #17a2b8); '
            'height:100%; width:{}%; border-radius:10px; '
            'text-align:center; color:white; font-size:10px; line-height:18px;">'
            '{}%</div></div>'
            '<small>{}/{} Rials</small>',
            percent, percent,
            f'{paid:,}', f'{total:,}'    # ← f-string به عنوان رشته امن
        )

    @admin.display(description=_('Due Date'))
    def payment_due_date_jalali(self, obj):
        if obj.payment_due_date:
            try:
                import jdatetime
                jalali = jdatetime.date.fromgregorian(date=obj.payment_due_date)
                if obj.status in ['pending', 'partially_paid'] and obj.payment_due_date < timezone.now().date():
                    return format_html(
                        '<span style="color:#dc3545; font-weight:bold;">⚠️ {}</span>',
                        jalali.strftime('%Y/%m/%d')
                    )
                return jalali.strftime('%Y/%m/%d')
            except ImportError:
                return obj.payment_due_date.strftime('%Y-%m-%d')
        return '-'

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')

    # ==================== Actions ====================

    actions = [
        'mark_as_paid', 'mark_as_cancelled',
        'convert_to_final',
        'export_csv',
    ]

    @admin.action(description=_('Mark selected as PAID'))
    def mark_as_paid(self, request, queryset):
        count = 0
        for invoice in queryset.filter(status__in=['pending', 'partially_paid', 'draft']):
            invoice.mark_as_paid()
            count += 1
        self.message_user(request, _(f'{count} invoice(s) marked as paid.'))

    @admin.action(description=_('Mark selected as CANCELLED'))
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.filter(
            status__in=['draft', 'pending', 'partially_paid']
        ).update(status='cancelled')
        self.message_user(request, _(f'{updated} invoice(s) cancelled.'), level='warning')

    @admin.action(description=_('Convert proforma to final'))
    def convert_to_final(self, request, queryset):
        count = 0
        for invoice in queryset.filter(invoice_type='proforma', status__in=['draft', 'pending']):
            invoice.convert_to_final()
            count += 1
        self.message_user(request, _(f'{count} proforma(s) converted to final.'))

    @admin.action(description=_('Export selected to CSV'))
    def export_csv(self, request, queryset):
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invoices_export.csv"'
        response.write('\ufeff'.encode('utf-8'))

        import csv
        writer = csv.writer(response)
        writer.writerow([
            'Invoice Number', 'User', 'Type', 'Status',
            'Total Amount', 'Paid Amount', 'Remaining',
            'Payment Method', 'Due Date', 'Created At'
        ])

        for invoice in queryset:
            writer.writerow([
                invoice.invoice_number,
                invoice.user.get_display_name() if invoice.user else 'N/A',
                invoice.invoice_type, invoice.status,
                int(invoice.total_amount), int(invoice.paid_amount),
                int(invoice.remaining_amount),
                invoice.payment_method or '-',
                invoice.payment_due_date.isoformat() if invoice.payment_due_date else '-',
                invoice.created_at.isoformat(),
            ])

        return response


# ============================================================
# InvoiceItem Admin
# ============================================================

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_link', 'product_name', 'description_short',
        'quantity', 'unit_price_display', 'discount_percent',
        'total_price_display', 'created_at_jalali',
    ]
    list_filter = ['created_at']
    search_fields = [
        'description', 'sku', 'invoice__invoice_number',
        'product__name',
    ]
    readonly_fields = ['id', 'total_price', 'created_at']
    autocomplete_fields = ['invoice', 'product']

    fieldsets = (
        (_('Relations'), {'fields': ('invoice', 'product')}),
        (_('Item Info'), {'fields': ('description', 'sku')}),
        (_('Pricing'), {
            'fields': ('quantity', 'unit_price', 'discount_percent', 'tax_percent', 'total_price')
        }),
        (_('Warranty'), {'fields': ('warranty_description',)}),
        (_('Notes'), {'fields': ('notes',)}),
    )

    list_per_page = 100

    @admin.display(description=_('Invoice'))
    def invoice_link(self, obj):
        return format_html(
            '<a href="{}"><code>{}</code></a>',
            f'/admin/financial/invoice/{obj.invoice.id}/change/',
            obj.invoice.invoice_number[:15]
        )

    @admin.display(description=_('Product'))
    def product_name(self, obj):
        if obj.product:
            return obj.product.name[:50]
        return '-'

    @admin.display(description=_('Description'))
    def description_short(self, obj):
        return obj.description[:60]

    @admin.display(description=_('Unit Price'))
    def unit_price_display(self, obj):
        return format_html('<b>{}</b>', f'{int(obj.unit_price):,}')

    @admin.display(description=_('Total'))
    def total_price_display(self, obj):
        return format_html(
            '<span style="color: #e94560; font-weight: bold;">{}</span>',
            f'{int(obj.total_price):,}'
        )

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')


# ============================================================
# Financial Transaction Admin
# ============================================================

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_number_short', 'user_info', 'type_badge',
        'amount_display', 'status_badge', 'payment_method_badge',
        'invoice_link', 'reference_code',
        'transaction_date_jalali',
    ]
    list_filter = [
        'transaction_type', 'status', 'payment_method',
        'transaction_date', 'verified_at',
    ]
    search_fields = [
        'transaction_number', 'reference_code',
        'user__email', 'user__mobile',
        'invoice__invoice_number', 'description',
    ]
    readonly_fields = [
        'id', 'transaction_number', 'amount',
        'verified_at', 'created_at', 'updated_at',
    ]
    autocomplete_fields = ['user', 'invoice', 'wallet', 'verified_by']

    fieldsets = (
        (_('Transaction Info'), {
            'fields': ('id', 'transaction_number', 'transaction_type', 'status')
        }),
        (_('Relations'), {
            'fields': ('user', 'invoice', 'wallet')
        }),
        (_('Payment Details'), {
            'fields': ('amount', 'payment_method', 'reference_code')
        }),
        (_('Verification'), {
            'fields': ('verified_at', 'verified_by', 'gateway_response')
        }),
        (_('Description'), {
            'fields': ('description',)
        }),
        (_('Timestamps'), {
            'fields': ('transaction_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    list_per_page = 100
    date_hierarchy = 'transaction_date'

    def has_add_permission(self, request):
        return False  # تراکنش فقط از طریق سیستم ایجاد بشه

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == 'verified':
            return False  # تراکنش تایید شده قابل ویرایش نیست
        return super().has_change_permission(request, obj)

    # ==================== List Display Methods ====================

    @admin.display(description=_('Trx #'))
    def transaction_number_short(self, obj):
        return format_html(
            '<code style="font-size: 11px;">{}</code>',
            obj.transaction_number[:20]
        )

    @admin.display(description=_('User'))
    def user_info(self, obj):
        if obj.user:
            return obj.user.get_display_name()
        return '-'

    @admin.display(description=_('Type'))
    def type_badge(self, obj):
        colors = {
            'payment': ('#dc3545', '💳'),
            'deposit': ('#28a745', '📥'),
            'withdraw': ('#ffc107', '📤'),
            'refund': ('#17a2b8', '↩️'),
            'commission': ('#6f42c1', '💸'),
            'adjustment': ('#fd7e14', '🔧'),
            'wallet_charge': ('#20c997', '💰'),
        }
        color, icon = colors.get(obj.transaction_type, ('#6c757d', '❓'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{} {}</span>',
            color, icon, obj.get_transaction_type_display()
        )

    @admin.display(description=_('Amount'))
    def amount_display(self, obj):
        is_credit = obj.transaction_type in ['deposit', 'refund', 'wallet_charge']
        color = '#28a745' if is_credit else '#dc3545'
        prefix = '+' if is_credit else '-'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {:,}</span>',
            color, prefix, int(obj.amount)
        )

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {
            'pending': ('#ffc107', '⏳'),
            'verified': ('#28a745', '✅'),
            'failed': ('#dc3545', '❌'),
            'refunded': ('#17a2b8', '↩️'),
        }
        color, icon = colors.get(obj.status, ('#6c757d', '❓'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )

    @admin.display(description=_('Method'))
    def payment_method_badge(self, obj):
        if obj.payment_method:
            return obj.get_payment_method_display()
        return '-'

    @admin.display(description=_('Invoice'))
    def invoice_link(self, obj):
        if obj.invoice:
            return format_html(
                '<a href="{}"><code>{}</code></a>',
                f'/admin/financial/invoice/{obj.invoice.id}/change/',
                obj.invoice.invoice_number[:12]
            )
        return '-'

    @admin.display(description=_('Date'))
    def transaction_date_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.transaction_date
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.transaction_date.strftime('%Y-%m-%d %H:%M')

    # ==================== Actions ====================

    actions = ['verify_selected', 'mark_as_failed']

    @admin.action(description=_('Verify selected transactions'))
    def verify_selected(self, request, queryset):
        count = 0
        for trx in queryset.filter(status='pending'):
            trx.status = 'verified'
            trx.verified_at = timezone.now()
            trx.verified_by = request.user
            trx.save()
            count += 1
        self.message_user(request, _(f'{count} transaction(s) verified.'))

    @admin.action(description=_('Mark selected as FAILED'))
    def mark_as_failed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='failed')
        self.message_user(request, _(f'{updated} transaction(s) marked as failed.'), level='warning')


# ============================================================
# Financial Report Admin
# ============================================================

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report_type_badge', 'format_badge',
        'date_range_display', 'generated_by_name',
        'summary_stats', 'created_at_jalali',
    ]
    list_filter = ['report_type', 'format', 'created_at']
    search_fields = ['title', 'generated_by__email', 'notes']
    readonly_fields = [
        'id', 'title', 'report_type', 'format',
        'from_date', 'to_date', 'generated_by',
        'parameters', 'data',
        'total_invoices', 'total_amount', 'total_paid',
        'total_discount', 'total_tax',
        'report_file', 'created_at',
    ]

    fieldsets = (
        (_('Report Info'), {
            'fields': ('title', 'report_type', 'format')
        }),
        (_('Date Range'), {
            'fields': ('from_date', 'to_date')
        }),
        (_('Summary'), {
            'fields': (
                'total_invoices', 'total_amount', 'total_paid',
                'total_discount', 'total_tax'
            )
        }),
        (_('Details'), {
            'fields': ('generated_by', 'parameters', 'data', 'notes'),
            'classes': ('collapse',)
        }),
        (_('File'), {
            'fields': ('report_file',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at',)
        }),
    )

    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Type'))
    def report_type_badge(self, obj):
        icons = {
            'daily': '📅', 'weekly': '📊', 'monthly': '📈',
            'quarterly': '📉', 'yearly': '🗓️', 'custom': '🔍',
        }
        return format_html(
            '{} {}', icons.get(obj.report_type, '📊'), obj.get_report_type_display()
        )

    @admin.display(description=_('Format'))
    def format_badge(self, obj):
        colors = {
            'json': '#28a745', 'csv': '#17a2b8',
            'excel': '#28a745', 'pdf': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            colors.get(obj.format, '#6c757d'), obj.format.upper()
        )

    @admin.display(description=_('Period'))
    def date_range_display(self, obj):
        try:
            import jdatetime
            from_date = jdatetime.date.fromgregorian(date=obj.from_date)
            to_date = jdatetime.date.fromgregorian(date=obj.to_date)
            return f"{from_date.strftime('%Y/%m/%d')} - {to_date.strftime('%Y/%m/%d')}"
        except ImportError:
            return f"{obj.from_date} - {obj.to_date}"

    @admin.display(description=_('By'))
    def generated_by_name(self, obj):
        if obj.generated_by:
            return obj.generated_by.get_display_name()
        return '-'

    @admin.display(description=_('Stats'))
    def summary_stats(self, obj):
        return format_html(
            '<b>{}</b> invoices<br/>'
            '<span style="color: #28a745;">{:,} paid</span><br/>'
            '<span style="color: #e94560;">{:,} disc</span>',
            obj.total_invoices, int(obj.total_paid), int(obj.total_discount)
        )

    @admin.display(description=_('Created'))
    def created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(
                datetime=obj.created_at
            ).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')