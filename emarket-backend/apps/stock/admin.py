from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import (
    Warehouse, ProductCategory, Brand, BrandSeries,
    Product, ProductImage, ProductDocument,
    InventoryItem, StockMovement,
)


# ============================================================
# Inline Models
# ============================================================

class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 0
    fields = ['product', 'quantity', 'reserved_quantity', 'status', 'shelf', 'batch_number']
    readonly_fields = ['reserved_quantity']
    show_change_link = True
    can_delete = False


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'image_preview', 'title', 'is_main', 'sort_order']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = _('Preview')


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1
    fields = ['title', 'doc_type', 'file']


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    fields = ['movement_type', 'quantity', 'from_warehouse', 'to_warehouse', 'created_at']
    readonly_fields = ['created_at']
    can_delete = False
    max_num = 0
    ordering = ['-created_at']


class SubWarehouseInline(admin.TabularInline):
    model = Warehouse
    fk_name = 'parent'
    extra = 0
    fields = ['code', 'name', 'warehouse_type', 'is_active']
    readonly_fields = ['code']
    show_change_link = True
    can_delete = False
    verbose_name = _('Sub Warehouse')
    verbose_name_plural = _('Sub Warehouses')


# ============================================================
# Warehouse Admin
# ============================================================

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'warehouse_type_badge', 'scope_badge',
        'parent_link', 'manager_name', 'stock_summary',
        'location_badge', 'is_active_badge',
    ]
    list_filter = [
        'warehouse_type', 'scope', 'is_active', 'is_public',
        'created_at',
    ]
    search_fields = ['code', 'name', 'address', 'phone', 'email']
    readonly_fields = ['id', 'current_items', 'created_at', 'updated_at']
    autocomplete_fields = ['parent', 'manager']
    filter_horizontal = ['staff']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'name', 'warehouse_type', 'scope', 'description')
        }),
        (_('Hierarchy'), {
            'fields': ('parent', 'manager', 'staff')
        }),
        (_('Location'), {
            'fields': ('address', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        (_('Contact'), {
            'fields': ('phone', 'email')
        }),
        (_('Capacity'), {
            'fields': ('capacity', 'current_items')
        }),
        (_('Specialization'), {
            'fields': ('specialized_hardware',),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_active', 'is_public')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [SubWarehouseInline, InventoryItemInline]

    @admin.display(description=_('Type'))
    def warehouse_type_badge(self, obj):
        colors = {
            'main': ('#28a745', '🏭'),
            'sub': ('#17a2b8', '📦'),
            'specialized': ('#6f42c1', '🔧'),
            'temporary': ('#ffc107', '⏳'),
        }
        color, icon = colors.get(obj.warehouse_type, ('#6c757d', '📦'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-size: 12px;">{} {}</span>',
            color, icon, obj.get_warehouse_type_display()
        )

    @admin.display(description=_('Scope'))
    def scope_badge(self, obj):
        if obj.scope == 'general':
            return format_html('🌐 General')
        return format_html('🎯 {}', obj.specialized_hardware or 'Specialized')

    @admin.display(description=_('Parent'))
    def parent_link(self, obj):
        if obj.parent:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/stock/warehouse/{obj.parent.id}/change/',
                obj.parent.name
            )
        return '-'

    @admin.display(description=_('Manager'))
    def manager_name(self, obj):
        if obj.manager:
            return obj.manager.get_display_name()
        return '-'

    @admin.display(description=_('Stock'))
    def stock_summary(self, obj):
        total = obj.inventory_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return format_html(
            '<b>{}</b> items',
            total
        )

    @admin.display(description=_('Location'))
    def location_badge(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">📍 View Map</a>',
                obj.latitude, obj.longitude
            )
        return '📍 No GPS'

    @admin.display(description=_('Active'))
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('✅ Active')
        return format_html('❌ Inactive')

    actions = ['activate_warehouses', 'deactivate_warehouses']

    @admin.action(description=_('Activate selected warehouses'))
    def activate_warehouses(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f'{updated} warehouse(s) activated.'))

    @admin.action(description=_('Deactivate selected warehouses'))
    def deactivate_warehouses(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f'{updated} warehouse(s) deactivated.'), level='warning')


# ============================================================
# Product Category Admin
# ============================================================

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category_type_badge', 'condition_badge',
        'parent_link', 'level', 'sort_order',
        'is_active', 'products_count',
    ]
    list_filter = ['category_type', 'condition', 'level', 'is_active', 'is_featured']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['level', 'created_at', 'updated_at']
    autocomplete_fields = ['parent']

    fieldsets = (
        (_('Basic'), {'fields': ('name', 'slug', 'category_type', 'condition')}),
        (_('Hierarchy'), {'fields': ('parent', 'level')}),
        (_('Display'), {'fields': ('description', 'icon', 'image')}),
        (_('Settings'), {'fields': ('sort_order', 'is_active', 'is_featured')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description=_('Type'))
    def category_type_badge(self, obj):
        colors = {
            'condition': '#28a745',
            'usage': '#17a2b8',
            'brand': '#ffc107',
            'type': '#6f42c1',
            'series': '#dc3545',
        }
        color = colors.get(obj.category_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.get_category_type_display()
        )

    @admin.display(description=_('Condition'))
    def condition_badge(self, obj):
        if obj.condition:
            return format_html(
                '<span style="color: #28a745;">{}</span>',
                obj.get_condition_display()
            )
        return '-'

    @admin.display(description=_('Parent'))
    def parent_link(self, obj):
        if obj.parent:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/stock/productcategory/{obj.parent.id}/change/',
                obj.parent.name
            )
        return '🏠 Root'

    @admin.display(description=_('Products'))
    def products_count(self, obj):
        descendants = obj.get_descendants(include_self=True)
        count = Product.objects.filter(category__in=descendants, is_active=True).count()
        return count


# ============================================================
# Brand Admin
# ============================================================

class BrandSeriesInline(admin.TabularInline):
    model = BrandSeries
    extra = 1
    fields = ['name', 'generation', 'year_released', 'is_active']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = [
        'logo_preview', 'name', 'persian_name',
        'country', 'is_partner_badge', 'popularity_score',
        'products_count', 'is_active',
    ]
    list_filter = ['is_active', 'is_partner', 'country']
    search_fields = ['name', 'persian_name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['popularity_score', 'created_at', 'updated_at']

    fieldsets = (
        (_('Basic'), {'fields': ('name', 'persian_name', 'slug', 'logo')}),
        (_('Details'), {'fields': ('website', 'country', 'description', 'warranty_info')}),
        (_('Status'), {'fields': ('is_active', 'is_partner', 'popularity_score')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    inlines = [BrandSeriesInline]

    @admin.display(description=_('Logo'))
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 80px;" />',
                obj.logo.url
            )
        return '🖼️ No Logo'

    @admin.display(description=_('Partner'))
    def is_partner_badge(self, obj):
        if obj.is_partner:
            return format_html('🤝 Official Partner')
        return '-'

    @admin.display(description=_('Products'))
    def products_count(self, obj):
        return obj.products.filter(is_active=True).count()


# ============================================================
# Brand Series Admin
# ============================================================

@admin.register(BrandSeries)
class BrandSeriesAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'brand', 'generation',
        'year_released', 'products_count', 'is_active',
    ]
    list_filter = ['brand', 'is_active', 'year_released']
    search_fields = ['name', 'brand__name', 'generation']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['brand', 'category']

    @admin.display(description=_('Full Name'))
    def full_name(self, obj):
        return obj.full_name

    @admin.display(description=_('Products'))
    def products_count(self, obj):
        return obj.products.filter(is_active=True).count()


# ============================================================
# Product Admin
# ============================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'main_image_preview', 'sku', 'name', 'condition_badge',
        'brand', 'category', 'price_info',
        'stock_summary', 'market_status_badge',
        'is_active',
    ]
    list_filter = [
        'condition', 'market_status', 'is_active', 'is_market_visible',
        'brand', 'category', 'created_at',
    ]
    search_fields = ['sku', 'name', 'model_number', 'part_number', 'processor']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = [
        'id', 'sku', 'created_by', 'created_at', 'updated_at',
        'market_quantity',
    ]
    autocomplete_fields = ['brand', 'series', 'category', 'created_by']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('sku', 'name', 'slug', 'condition')
        }),
        (_('Categorization'), {
            'fields': ('category', 'brand', 'series', 'model_number', 'part_number')
        }),
        (_('Processor'), {
            'fields': (
                'processor', 'processor_cores', 'processor_threads',
                'processor_speed', 'processor_count'
            ),
            'classes': ('collapse',)
        }),
        (_('Memory'), {
            'fields': ('ram', 'ram_slots_total', 'ram_slots_used', 'ram_max'),
            'classes': ('collapse',)
        }),
        (_('Storage'), {
            'fields': ('storage', 'storage_type', 'total_storage'),
            'classes': ('collapse',)
        }),
        (_('Network & GPU'), {
            'fields': ('network', 'network_ports', 'gpu', 'gpu_memory'),
            'classes': ('collapse',)
        }),
        (_('Physical'), {
            'fields': (
                'form_factor', 'dimensions', 'weight',
                'power_supply', 'power_consumption', 'ports'
            ),
            'classes': ('collapse',)
        }),
        (_('Warranty'), {
            'fields': ('warranty', 'warranty_expiry')
        }),
        (_('Pricing'), {
            'fields': ('cost_price', 'selling_price', 'market_price', 'discount_percent', 'currency')
        }),
        (_('Media'), {
            'fields': ('main_image', 'additional_specs')
        }),
        (_('Market'), {
            'fields': (
                'market_status', 'market_quantity', 'is_market_visible',
                'market_description', 'market_tags'
            )
        }),
        (_('Settings'), {
            'fields': ('min_stock_alert', 'is_active', 'created_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ProductImageInline, ProductDocumentInline, InventoryItemInline]

    @admin.display(description=_('Image'))
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px;" />',
                obj.main_image.url
            )
        return '🖼️'

    @admin.display(description=_('Condition'))
    def condition_badge(self, obj):
        colors = {
            'new': '#28a745',
            'like_new': '#17a2b8',
            'used': '#ffc107',
            'refurbished': '#6f42c1',
            'damaged': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            colors.get(obj.condition, '#6c757d'),
            obj.get_condition_display()
        )

    @admin.display(description=_('Price'))
    def price_info(self, obj):
        price = obj.market_price or obj.selling_price
        if obj.discount_percent > 0:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{:,.0f}</span> '
                '<span style="color: #e94560; font-weight: bold;">{:,.0f} (-{}%)</span>',
                price, obj.final_market_price, int(obj.discount_percent)
            )
        return '{:,.0f}'.format(price)

    @admin.display(description=_('Stock'))
    def stock_summary(self, obj):
        total = obj.total_stock
        available = obj.available_stock
        market = obj.market_quantity

        return format_html(
            'Total: <b>{}</b><br/>'
            '<span style="color: #28a745;">Available: {}</span><br/>'
            '<span style="color: #17a2b8;">Market: {}</span>',
            total, available, market
        )

    @admin.display(description=_('Market'))
    def market_status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'published': '#28a745',
            'archived': '#ffc107',
            'sold_out': '#dc3545',
        }
        icon = '✅' if obj.is_market_visible else '❌'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{} {}</span>',
            colors.get(obj.market_status, '#6c757d'),
            icon, obj.get_market_status_display()
        )

    actions = [
        'publish_to_market', 'remove_from_market',
        'activate_products', 'deactivate_products',
    ]

    @admin.action(description=_('Publish selected to market'))
    def publish_to_market(self, request, queryset):
        for product in queryset:
            if product.available_stock > 0:
                product.market_status = 'published'
                product.is_market_visible = True
                product.market_quantity = min(product.available_stock, 10)
                product.save()
        self.message_user(request, _('Selected products published to market.'))

    @admin.action(description=_('Remove selected from market'))
    def remove_from_market(self, request, queryset):
        queryset.update(
            market_status='draft',
            is_market_visible=False,
            market_quantity=0
        )
        self.message_user(request, _('Selected products removed from market.'), level='warning')

    @admin.action(description=_('Activate selected products'))
    def activate_products(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, _('Products activated.'))

    @admin.action(description=_('Deactivate selected products'))
    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, _('Products deactivated.'), level='warning')


# ============================================================
# Inventory Admin
# ============================================================

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = [
        'product_sku', 'product_name', 'warehouse_code',
        'quantity', 'reserved_quantity', 'available_qty',
        'status_badge', 'location', 'low_stock_alert',
        'last_checked_at',
    ]
    list_filter = ['status', 'warehouse', 'received_date']
    search_fields = [
        'product__sku', 'product__name', 'warehouse__code',
        'batch_number', 'location_barcode',
    ]
    readonly_fields = ['last_checked_at', 'created_at', 'updated_at']
    autocomplete_fields = ['warehouse', 'product']

    fieldsets = (
        (_('Relations'), {'fields': ('warehouse', 'product')}),
        (_('Quantity'), {'fields': ('quantity', 'reserved_quantity', 'minimum_quantity')}),
        (_('Location'), {'fields': ('shelf', 'aisle', 'section', 'location_barcode')}),
        (_('Status'), {'fields': ('status',)}),
        (_('Batch'), {'fields': ('batch_number', 'received_date', 'expiry_date')}),
        (_('Notes'), {'fields': ('notes',)}),
        (_('Audit'), {'fields': ('last_checked_at', 'last_checked_by', 'created_at', 'updated_at')}),
    )

    inlines = [StockMovementInline]

    @admin.display(description=_('SKU'))
    def product_sku(self, obj):
        return obj.product.sku

    @admin.display(description=_('Product'))
    def product_name(self, obj):
        return obj.product.name[:50]

    @admin.display(description=_('Warehouse'))
    def warehouse_code(self, obj):
        return obj.warehouse.code

    @admin.display(description=_('Available'))
    def available_qty(self, obj):
        qty = obj.available_quantity
        if qty <= 0:
            return format_html('<span style="color: #dc3545;">0</span>')
        return qty

    @admin.display(description=_('Status'))
    def status_badge(self, obj):
        colors = {
            'in_stock': '#28a745',
            'reserved': '#17a2b8',
            'in_transit': '#ffc107',
            'damaged': '#dc3545',
            'returned': '#6f42c1',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )

    @admin.display(description=_('Location'))
    def location(self, obj):
        return obj.location if obj.location != '-' else '-'

    @admin.display(description=_('Alert'))
    def low_stock_alert(self, obj):
        if obj.is_low_stock:
            return format_html('⚠️ Low Stock')
        return '✅'

    actions = ['mark_as_damaged', 'mark_as_in_stock']

    @admin.action(description=_('Mark as damaged'))
    def mark_as_damaged(self, request, queryset):
        queryset.update(status='damaged')
        self.message_user(request, _('Items marked as damaged.'), level='warning')

    @admin.action(description=_('Mark as in stock'))
    def mark_as_in_stock(self, request, queryset):
        queryset.update(status='in_stock')
        self.message_user(request, _('Items marked as in stock.'))


# ============================================================
# Stock Movement Admin
# ============================================================

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'movement_type_badge', 'product_info', 'quantity',
        'warehouse_info', 'reference', 'performed_by',
        'created_at',
    ]
    list_filter = ['movement_type', 'created_at']
    search_fields = [
        'inventory_item__product__sku', 'reference',
        'inventory_item__warehouse__code',
    ]
    readonly_fields = [
        'id', 'inventory_item', 'movement_type', 'quantity',
        'from_warehouse', 'to_warehouse', 'performed_by',
        'created_at',
    ]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description=_('Type'))
    def movement_type_badge(self, obj):
        colors = {
            'in': '#28a745',
            'out': '#dc3545',
            'transfer': '#17a2b8',
            'reserve': '#ffc107',
            'unreserve': '#6f42c1',
            'adjustment': '#fd7e14',
            'return': '#20c997',
            'damaged': '#e83e8c',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            colors.get(obj.movement_type, '#6c757d'),
            obj.get_movement_type_display()
        )

    @admin.display(description=_('Product'))
    def product_info(self, obj):
        return f"{obj.inventory_item.product.sku} - {obj.inventory_item.product.name[:40]}"

    @admin.display(description=_('Warehouse'))
    def warehouse_info(self, obj):
        if obj.from_warehouse and obj.to_warehouse:
            return format_html(
                '{} → {}',
                obj.from_warehouse.code, obj.to_warehouse.code
            )
        elif obj.from_warehouse:
            return format_html('From: {}', obj.from_warehouse.code)
        elif obj.to_warehouse:
            return format_html('To: {}', obj.to_warehouse.code)
        return '-'