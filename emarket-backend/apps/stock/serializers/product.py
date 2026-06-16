from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.stock.models import Product, ProductImage, ProductDocument
from apps.stock.serializers.brand import BrandSerializer, BrandSeriesSerializer
from apps.stock.serializers.category import ProductCategorySerializer


class ProductImageSerializer(serializers.ModelSerializer):
    """سریالایزر تصاویر محصول"""

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'title', 'is_main', 'sort_order']


class ProductDocumentSerializer(serializers.ModelSerializer):
    """سریالایزر مستندات محصول"""

    class Meta:
        model = ProductDocument
        fields = ['id', 'title', 'file', 'doc_type']


class ProductListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست محصولات (خلاصه)"""
    condition_display = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    total_stock = serializers.IntegerField(read_only=True)
    market_status_display = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug',
            'condition', 'condition_display',
            'brand_name', 'model_number',
            'main_image',
            'selling_price', 'market_price', 'final_price',
            'total_stock', 'market_quantity', 'market_status', 'market_status_display',
            'is_active', 'is_market_visible',
            'created_at',
        ]

    def get_condition_display(self, obj):
        return {
            'code': obj.condition,
            'label': obj.get_condition_display(),
            'badge': {
                'new': '🟢',
                'like_new': '🔵',
                'used': '🟡',
                'refurbished': '🟠',
                'damaged': '🔴',
            }.get(obj.condition, '⚪')
        }

    def get_brand_name(self, obj):
        if obj.brand:
            return obj.brand.persian_name or obj.brand.name
        return None

    def get_market_status_display(self, obj):
        return {
            'code': obj.market_status,
            'label': obj.get_market_status_display(),
        }


class ProductSerializer(serializers.ModelSerializer):
    """سریالایزر کامل محصول"""
    condition_display = serializers.SerializerMethodField()

    # 🎯 تغییر نام فیلدهای نمایشی به _info
    brand_info = BrandSerializer(source='brand', read_only=True)
    series_info = BrandSeriesSerializer(source='series', read_only=True)
    category_info = ProductCategorySerializer(source='category', read_only=True)

    images = ProductImageSerializer(many=True, read_only=True)
    documents = ProductDocumentSerializer(many=True, read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    available_stock = serializers.IntegerField(read_only=True)
    final_market_price = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug',
            'condition', 'condition_display',

            # 🎯 اضافه کردن فیلدهای اصلی (برای نوشتن ID) و فیلدهای info (برای خواندن اطلاعات کامل)
            'category', 'category_info',
            'brand', 'brand_info',
            'series', 'series_info',

            'model_number', 'part_number',
            # Specs
            'processor', 'processor_cores', 'processor_threads',
            'processor_speed', 'processor_count',
            'ram', 'ram_slots_total', 'ram_slots_used', 'ram_max',
            'storage', 'storage_type', 'total_storage',
            'network', 'network_ports',
            'gpu', 'gpu_memory',
            'power_supply', 'power_consumption',
            'form_factor', 'dimensions', 'weight',
            'ports', 'additional_specs',
            # Warranty
            'warranty', 'warranty_expiry',
            # Media
            'main_image', 'images', 'documents',
            # Pricing
            'cost_price', 'selling_price', 'market_price',
            'discount_percent', 'final_market_price', 'currency',
            # Market
            'market_status', 'market_quantity', 'is_market_visible',
            'market_description', 'market_tags',
            # Stock
            'total_stock', 'available_stock', 'min_stock_alert',
            # Meta
            'is_active', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'sku', 'slug', 'created_by', 'created_at', 'updated_at']

    def get_condition_display(self, obj):
        return {
            'code': obj.condition,
            'label': obj.get_condition_display(),
        }


class ProductCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد محصول"""
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'name', 'condition', 'category', 'brand', 'series',
            'model_number', 'part_number',
            # Specs
            'processor', 'processor_cores', 'processor_threads',
            'processor_speed', 'processor_count',
            'ram', 'ram_slots_total', 'ram_slots_used', 'ram_max',
            'storage', 'storage_type', 'total_storage',
            'network', 'network_ports',
            'gpu', 'gpu_memory',
            'power_supply', 'power_consumption',
            'form_factor', 'dimensions', 'weight',
            'ports', 'additional_specs',
            # Warranty
            'warranty', 'warranty_expiry',
            # Media
            'main_image', 'images',
            # Pricing
            'cost_price', 'selling_price',
            'currency', 'discount_percent',
            # Market
            'market_description', 'market_tags',
            'min_stock_alert', 'is_active',
        ]

    def create(self, validated_data):
        images = validated_data.pop('images', [])

        # تولید SKU
        import uuid
        validated_data['sku'] = f"XIG-{uuid.uuid4().hex[:8].upper()}"
        validated_data['created_by'] = self.context['request'].user

        product = super().create(validated_data)

        # ذخیره تصاویر اضافی
        for i, image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_main=(i == 0 and not product.main_image),
                sort_order=i
            )

        return product


class ProductMarketSerializer(serializers.Serializer):
    """
    سریالایزر تنظیم انتشار در مارکت
    """
    market_quantity = serializers.IntegerField(
        required=True,
        min_value=1,
        error_messages={
            'required': _('Market quantity is required.'),
            'min_value': _('Must be at least 1.'),
        }
    )
    market_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False
    )
    market_description = serializers.CharField(required=False)
    market_tags = serializers.CharField(required=False)

    def validate_market_quantity(self, value):
        """بررسی موجودی کافی"""
        product = self.context.get('product')
        if product and value > product.available_stock:
            raise serializers.ValidationError(
                _(f'Not enough stock. Available: {product.available_stock}')
            )
        return value