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
            'created_at',
        ]

    def get_main_image(self, obj):
        media = obj.media.filter(is_main=True).first()
        if not media:
            media = obj.media.first()
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

    media = ProductMediaSerializer(many=True, read_only=True)
    rating_summary = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = MarketProduct
        fields = [
            'id', 'title', 'slug', 'short_description', 'full_description',
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

    def get_rating_summary(self, obj):
        return {
            'overall': {
                'avg': float(obj.avg_rating),
                'count': obj.rating_count,
                'stars': '⭐' * int(obj.avg_rating),
            },
            'breakdown': {
                'value_for_money': float(obj.avg_value_for_money),
                'quality': float(obj.avg_quality),
                'performance': float(obj.avg_performance),
            },
            'distribution': self._get_rating_distribution(obj),
        }

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