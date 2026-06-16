from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.market.models import MarketProduct
from apps.market.serializers.rating import RatingSummarySerializer
from apps.market.serializers.review import ReviewListSerializer
from apps.market.serializers.media import ProductMediaSerializer


class MarketProductListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست محصولات مارکت"""
    final_price = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    main_image = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    rating_summary = serializers.SerializerMethodField()
    discount_badge = serializers.SerializerMethodField()
    stock_product_id = serializers.UUIDField(source='stock_product.id', read_only=True)

    class Meta:
        model = MarketProduct
        fields = [
            'id', 'title', 'slug', 'short_description',
            'market_price', 'discount_price', 'discount_percent',
            'final_price', 'has_discount', 'discount_badge',
            'is_in_stock', 'available_quantity',
            'main_image', 'brand_name', 'category_name',
            'avg_rating', 'rating_count', 'rating_summary',
            'views_count', 'sales_count', 'wishlist_count',
            'is_featured', 'is_bestseller',
            'created_at','stock_product_id'
        ]

    def get_main_image(self, obj):
        # ۱. ابتدا بررسی می‌کنیم آیا خود MarketProduct تصویر اختصاصی دارد؟
        media = obj.media.filter(is_main=True).first()
        if not media:
            media = obj.media.first()

        # ۲. اگر در مارکت تصویری نبود، به سراغ کالای متصل شده در انبار می‌رویم
        if not media and obj.stock_product:
            # فرض بر این است که مدل انبار دارای فیلد main_image است یا تصاویری در obj.stock_product.images دارد
            if getattr(obj.stock_product, 'main_image', None):
                image_url = obj.stock_product.main_image.url
            else:
                # جستجو در گالری تصاویر انبار
                stock_img = obj.stock_product.images.filter(is_main=True).first()
                if not stock_img:
                    stock_img = obj.stock_product.images.first()
                if stock_img and stock_img.image:
                    image_url = stock_img.image.url
                else:
                    return None

            # ساخت URL کامل برای تصویر انبار
            request = self.context.get('request')
            if request and image_url:
                return request.build_absolute_uri(image_url)
            return image_url

        # ۳. اگر در خود مارکت تصویر بود، آن را برمی‌گردانیم
        if media and media.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(media.image.url)
            return media.image.url

        return None

    def get_brand_name(self, obj):
        sp = obj.stock_product
        if sp and sp.brand:
            return sp.brand.persian_name or sp.brand.name
        return None

    def get_category_name(self, obj):
        sp = obj.stock_product
        if sp and sp.category:
            return sp.category.name
        return None

    def get_rating_summary(self, obj):
        return {
            'avg': float(obj.avg_rating),
            'count': obj.rating_count,
            'stars': '⭐' * int(obj.avg_rating),
            'empty_stars': '☆' * (5 - int(obj.avg_rating)),
        }

    def get_discount_badge(self, obj):
        if obj.has_discount:
            if obj.discount_percent > 0:
                return f'-{int(obj.discount_percent)}%'
            return 'OFF'
        return None


class MarketProductSerializer(serializers.ModelSerializer):
    """سریالایزر کامل محصول مارکت"""
    final_price = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    has_discount = serializers.BooleanField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    stock_info = serializers.DictField(read_only=True)
    stock_product_id = serializers.UUIDField(source='stock_product.id', read_only=True)
    media = serializers.SerializerMethodField()
    rating_summary = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = MarketProduct
        fields = [
            'id', 'stock_product_id','title', 'slug', 'short_description', 'full_description',
            'market_price', 'discount_price', 'discount_percent',
            'discount_start', 'discount_end',
            'final_price', 'has_discount', 'is_in_stock',
            'available_quantity', 'min_order_quantity', 'max_order_quantity',
            'stock_info', 'media', 'tags',
            'avg_rating', 'rating_count',
            'avg_value_for_money', 'avg_quality', 'avg_performance',
            'rating_summary', 'recent_reviews', 'comments_count',
            'views_count', 'sales_count', 'wishlist_count',
            'is_active', 'is_featured', 'is_bestseller',
            'meta_title', 'meta_description', 'meta_keywords',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'views_count', 'sales_count', 'wishlist_count',
            'avg_rating', 'rating_count', 'created_at', 'updated_at',
        ]


    def get_media(self, obj):
        # اگر مارکت مدیای اختصاصی دارد
        if obj.media.exists():
            return ProductMediaSerializer(obj.media.all(), many=True, context=self.context).data

        # در غیر این صورت تصاویر انبار را با فرمت مشابه برگردان
        if obj.stock_product and obj.stock_product.images.exists():
            stock_images = obj.stock_product.images.all()
            result = []
            request = self.context.get('request')
            for img in stock_images:
                url = request.build_absolute_uri(img.image.url) if request else img.image.url
                result.append({
                    'id': str(img.id),
                    'image': url,
                    'is_main': img.is_main,
                    # سایر فیلدهای مورد نیاز
                })
            return result

        return []

    def get_recent_reviews(self, obj):
        reviews = obj.reviews.filter(status='published').order_by('-created_at')[:5]
        return ReviewListSerializer(reviews, many=True, context=self.context).data

    def get_comments_count(self, obj):
        return obj.comments.filter(status='active').count()

    def _get_rating_distribution(self, obj):
        """توزیع امتیازات (چندتا ۵ ستاره، ۴ ستاره و...)"""
        from django.db.models import Count
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        stats = obj.ratings.filter(is_active=True).values('overall').annotate(
            count=Count('overall')
        )

        for stat in stats:
            distribution[stat['overall']] = stat['count']

        return distribution


class MarketProductCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد محصول در مارکت"""

    class Meta:
        model = MarketProduct
        fields = [
            'title', 'stock_product', 'short_description', 'full_description',
            'market_price', 'discount_price', 'discount_percent',
            'discount_start', 'discount_end',
            'min_order_quantity', 'max_order_quantity',
            'tags', 'meta_title', 'meta_description', 'meta_keywords',
            'is_active', 'is_featured',
        ]

    def validate_stock_product(self, value):
        """بررسی اینکه محصول قبلاً توی مارکت نیست"""
        if MarketProduct.objects.filter(stock_product=value).exists():
            raise serializers.ValidationError(_('This product is already in market.'))

        if not value.is_market_visible:
            raise serializers.ValidationError(_('This product is not available for market.'))

        if value.market_quantity <= 0:
            raise serializers.ValidationError(_('Product has no market quantity.'))

        return value

    def validate_market_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(_('Price must be positive.'))
        return value