import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.stock.enums import ProductCondition, MarketListingStatus


class Product(models.Model):
    """
    مدل اصلی محصول

    ویژگی‌ها:
    - مشخصات کامل فنی
    - قابلیت انتشار در مارکت
    - مدیریت تعداد در انبار vs مارکت
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # ==================== Basic Info ====================
    sku = models.CharField(
        _('SKU'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Stock Keeping Unit - unique product code')
    )

    name = models.CharField(
        _('Product Name'),
        max_length=300,
        db_index=True
    )

    slug = models.SlugField(_('Slug'), max_length=350, unique=True)

    # ==================== Categorization ====================
    condition = models.CharField(
        _('Condition'),
        max_length=20,
        choices=ProductCondition.choices,
        default=ProductCondition.NEW,
        db_index=True
    )

    category = models.ForeignKey(
        'stock.ProductCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Category'),
        help_text=_('Lowest level category (series)')
    )

    brand = models.ForeignKey(
        'stock.Brand',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Brand')
    )

    series = models.ForeignKey(
        'stock.BrandSeries',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Series')
    )

    # ==================== Technical Specs ====================
    # عمومی
    model_number = models.CharField(
        _('Model Number'),
        max_length=200,
        blank=True,
        help_text=_('Manufacturer model number')
    )

    part_number = models.CharField(
        _('Part Number'),
        max_length=200,
        blank=True,
        help_text=_('Manufacturer part number')
    )

    # پردازنده
    processor = models.CharField(
        _('Processor'),
        max_length=200,
        blank=True,
        help_text=_('e.g., Intel Xeon Gold 6248R')
    )

    processor_cores = models.PositiveSmallIntegerField(
        _('Cores'),
        null=True,
        blank=True
    )

    processor_threads = models.PositiveSmallIntegerField(
        _('Threads'),
        null=True,
        blank=True
    )

    processor_speed = models.CharField(
        _('Base Speed'),
        max_length=50,
        blank=True,
        help_text=_('e.g., 3.0 GHz')
    )

    processor_count = models.PositiveSmallIntegerField(
        _('Processor Count'),
        default=1,
        help_text=_('Number of physical CPUs')
    )

    # حافظه RAM
    ram = models.CharField(
        _('RAM'),
        max_length=100,
        blank=True,
        help_text=_('e.g., 64GB DDR4 ECC')
    )

    ram_slots_total = models.PositiveSmallIntegerField(
        _('Total RAM Slots'),
        null=True,
        blank=True
    )

    ram_slots_used = models.PositiveSmallIntegerField(
        _('Used RAM Slots'),
        null=True,
        blank=True
    )

    ram_max = models.CharField(
        _('Max RAM'),
        max_length=50,
        blank=True
    )

    # ذخیره‌سازی
    storage = models.TextField(
        _('Storage'),
        blank=True,
        help_text=_('Storage configuration details')
    )

    storage_type = models.CharField(
        _('Storage Type'),
        max_length=100,
        blank=True,
        help_text=_('e.g., SSD, HDD, NVMe')
    )

    total_storage = models.CharField(
        _('Total Storage'),
        max_length=50,
        blank=True,
        help_text=_('e.g., 2TB SSD + 4TB HDD')
    )

    # شبکه
    network = models.TextField(
        _('Network'),
        blank=True,
        help_text=_('Network interfaces')
    )

    network_ports = models.PositiveSmallIntegerField(
        _('Network Ports'),
        null=True,
        blank=True
    )

    # گرافیک
    gpu = models.CharField(
        _('GPU'),
        max_length=200,
        blank=True
    )

    gpu_memory = models.CharField(
        _('GPU Memory'),
        max_length=50,
        blank=True
    )

    # قدرت
    power_supply = models.CharField(
        _('Power Supply'),
        max_length=200,
        blank=True,
        help_text=_('PSU specs')
    )

    power_consumption = models.CharField(
        _('Power Consumption'),
        max_length=50,
        blank=True,
        help_text=_('e.g., 750W')
    )

    # ابعاد و وزن
    form_factor = models.CharField(
        _('Form Factor'),
        max_length=50,
        blank=True,
        help_text=_('e.g., 1U, 2U, Tower, Mini')
    )

    dimensions = models.CharField(
        _('Dimensions'),
        max_length=100,
        blank=True,
        help_text=_('W x D x H in mm')
    )

    weight = models.CharField(
        _('Weight'),
        max_length=50,
        blank=True,
        help_text=_('in kg')
    )

    # پورت‌ها
    ports = models.TextField(
        _('Ports & Interfaces'),
        blank=True
    )

    # مشخصات اضافی (JSON)
    additional_specs = models.JSONField(
        _('Additional Specifications'),
        default=dict,
        blank=True,
        help_text=_('Any other technical details')
    )

    # ==================== Warranty ====================
    warranty = models.CharField(
        _('Warranty'),
        max_length=200,
        blank=True,
        help_text=_('e.g., 3 Years Manufacturer Warranty')
    )

    warranty_expiry = models.DateField(
        _('Warranty Expiry'),
        null=True,
        blank=True
    )

    # ==================== Media ====================
    main_image = models.ImageField(
        _('Main Image'),
        upload_to='products/images/%Y/%m/',
        null=True,
        blank=True
    )

    # ==================== Pricing ====================
    cost_price = models.DecimalField(
        _('Cost Price'),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_('Purchase cost for inventory')
    )

    selling_price = models.DecimalField(
        _('Selling Price'),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text=_('Base selling price')
    )

    market_price = models.DecimalField(
        _('Market Price'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Price shown in marketplace (can be different)')
    )

    discount_percent = models.DecimalField(
        _('Discount %'),
        max_digits=5,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(
        _('Currency'),
        max_length=3,
        default='IRR',
        help_text=_('IRR, USD, EUR')
    )

    # ==================== Market Listing ====================
    market_status = models.CharField(
        _('Market Status'),
        max_length=20,
        choices=MarketListingStatus.choices,
        default=MarketListingStatus.DRAFT,
        db_index=True
    )

    market_quantity = models.PositiveIntegerField(
        _('Market Quantity'),
        default=0,
        help_text=_('Number of units available in marketplace')
    )

    is_market_visible = models.BooleanField(
        _('Visible in Market'),
        default=False,
        help_text=_('Show this product in online marketplace')
    )

    market_description = models.TextField(
        _('Market Description'),
        blank=True,
        help_text=_('Description for marketplace listing')
    )

    market_tags = models.CharField(
        _('Tags'),
        max_length=500,
        blank=True,
        help_text=_('Comma-separated tags for search')
    )

    # ==================== Meta ====================
    is_active = models.BooleanField(_('Active'), default=True, db_index=True)

    min_stock_alert = models.PositiveIntegerField(
        _('Min Stock Alert'),
        default=5,
        help_text=_('Alert when stock falls below this number')
    )

    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_products'
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['condition', 'is_active']),
            models.Index(fields=['market_status', 'is_market_visible']),
            models.Index(fields=['brand', 'series']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    @property
    def total_stock(self):
        """کل موجودی در همه انبارها"""
        return self.inventory_items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def available_stock(self):
        """موجودی قابل فروش (کل - رزرو شده)"""
        from apps.stock.enums import InventoryStatus
        total = self.inventory_items.filter(
            status=InventoryStatus.IN_STOCK
        ).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        return total

    @property
    def market_available(self):
        """تعداد موجود در مارکت"""
        return self.market_quantity

    @property
    def is_in_stock(self):
        return self.available_stock > 0

    @property
    def final_market_price(self):
        """قیمت نهایی با تخفیف"""
        if self.market_price:
            base = self.market_price
        else:
            base = self.selling_price

        if self.discount_percent > 0:
            return base * (1 - self.discount_percent / 100)
        return base

    def allocate_to_market(self, quantity):
        """
        تخصیص تعداد به مارکت
        از انبار کم نمیشه، فقط market_quantity زیاد میشه
        """
        if quantity > self.available_stock:
            raise ValueError(_('Not enough stock available'))

        self.market_quantity += quantity
        self.is_market_visible = True
        self.save(update_fields=['market_quantity', 'is_market_visible'])
        return self.market_quantity

    def return_from_market(self, quantity):
        """برگشت از مارکت به انبار"""
        if quantity > self.market_quantity:
            raise ValueError(_('Not enough quantity in market'))

        self.market_quantity -= quantity
        if self.market_quantity <= 0:
            self.is_market_visible = False
        self.save(update_fields=['market_quantity', 'is_market_visible'])
        return self.market_quantity


class ProductImage(models.Model):
    """تصاویر محصول"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        _('Image'),
        upload_to='products/images/%Y/%m/'
    )

    title = models.CharField(_('Title'), max_length=200, blank=True)

    is_main = models.BooleanField(_('Main Image'), default=False)

    sort_order = models.PositiveIntegerField(_('Sort Order'), default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"Image for {self.product.sku}"


class ProductDocument(models.Model):
    """مستندات محصول (Datasheet, Manual)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    title = models.CharField(_('Title'), max_length=200)

    file = models.FileField(
        _('File'),
        upload_to='products/documents/%Y/%m/'
    )

    doc_type = models.CharField(
        _('Document Type'),
        max_length=50,
        choices=[
            ('datasheet', _('Datasheet')),
            ('manual', _('Manual')),
            ('warranty', _('Warranty Card')),
            ('certificate', _('Certificate')),
            ('other', _('Other')),
        ],
        default='other'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_documents'
        ordering = ['doc_type', 'title']

    def __str__(self):
        return f"{self.title} - {self.product.sku}"