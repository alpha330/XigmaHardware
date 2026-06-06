import logging
from django.db import transaction as db_transaction
from django.db.models import Q, F, Avg, Sum, Count,Min,Max
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.market.models import MarketProduct
from apps.stock.models import Product as StockProduct

logger = logging.getLogger(__name__)


class MarketService:
    """
    سرویس مدیریت محصولات مارکت

    عملیات:
    - انتقال محصول از Stock به Market
    - بروزرسانی موجودی
    - جستجو و فیلتر
    - مدیریت تخفیف‌ها
    - محصولات ویژه و پرفروش
    """

    # ==================== Product Management ====================

    @classmethod
    @db_transaction.atomic
    def publish_to_market(cls, stock_product, market_data):
        """
        انتشار محصول از انبار به مارکت

        Args:
            stock_product: محصول انبار
            market_data: داده‌های مارکت

        Returns:
            MarketProduct
        """
        # اعتبارسنجی
        if not stock_product.is_market_visible:
            raise ValueError(_('Product is not available for market.'))

        if stock_product.market_quantity <= 0:
            raise ValueError(_('Product has no market quantity.'))

        if MarketProduct.objects.filter(stock_product=stock_product).exists():
            raise ValueError(_('Product already in market.'))

        # ایجاد محصول مارکت
        market_product = MarketProduct.objects.create(
            stock_product=stock_product,
            title=market_data.get('title', stock_product.name),
            short_description=market_data.get('short_description', ''),
            full_description=market_data.get('full_description', ''),
            market_price=market_data.get('market_price', stock_product.final_market_price),
            discount_price=market_data.get('discount_price'),
            discount_percent=market_data.get('discount_percent', 0),
            discount_start=market_data.get('discount_start'),
            discount_end=market_data.get('discount_end'),
            available_quantity=stock_product.market_quantity,
            min_order_quantity=market_data.get('min_order_quantity', 1),
            max_order_quantity=market_data.get('max_order_quantity', 10),
            tags=market_data.get('tags', ''),
            meta_title=market_data.get('meta_title', ''),
            meta_description=market_data.get('meta_description', ''),
            meta_keywords=market_data.get('meta_keywords', ''),
            is_active=market_data.get('is_active', True),
            is_featured=market_data.get('is_featured', False),
        )

        logger.info(
            f"Product published to market: {market_product.title} "
            f"(Stock: {stock_product.sku})"
        )

        return market_product

    @classmethod
    @db_transaction.atomic
    def sync_stock_quantity(cls, market_product):
        """
        همگام‌سازی موجودی مارکت با انبار

        Args:
            market_product: محصول مارکت
        """
        stock_qty = market_product.stock_product.market_quantity

        if market_product.available_quantity != stock_qty:
            old_qty = market_product.available_quantity
            market_product.available_quantity = stock_qty
            market_product.save(update_fields=['available_quantity', 'updated_at'])

            logger.info(
                f"Stock synced for {market_product.slug}: {old_qty} -> {stock_qty}"
            )

        # اگر موجودی صفر شد، غیرفعال کن
        if stock_qty <= 0 and market_product.is_active:
            market_product.is_active = False
            market_product.save(update_fields=['is_active'])
            logger.info(f"Product {market_product.slug} deactivated (out of stock)")

    @classmethod
    @db_transaction.atomic
    def update_market_product(cls, market_product, data):
        """
        بروزرسانی محصول مارکت

        Args:
            market_product: محصول
            data: داده‌های جدید

        Returns:
            MarketProduct
        """
        allowed_fields = [
            'title', 'short_description', 'full_description',
            'market_price', 'discount_price', 'discount_percent',
            'discount_start', 'discount_end',
            'min_order_quantity', 'max_order_quantity',
            'tags', 'meta_title', 'meta_description', 'meta_keywords',
            'is_active', 'is_featured', 'is_bestseller', 'priority',
        ]

        for field in allowed_fields:
            if field in data:
                setattr(market_product, field, data[field])

        market_product.save()

        logger.info(f"Market product updated: {market_product.slug}")

        return market_product

    @classmethod
    @db_transaction.atomic
    def apply_discount(cls, market_product, discount_percent=None, discount_price=None,
                       start_date=None, end_date=None):
        """
        اعمال تخفیف روی محصول

        Args:
            market_product: محصول
            discount_percent: درصد تخفیف
            discount_price: قیمت تخفیف خورده
            start_date: شروع
            end_date: پایان

        Returns:
            MarketProduct
        """
        if discount_percent is not None:
            if not 0 <= discount_percent <= 100:
                raise ValueError(_('Discount must be between 0 and 100.'))
            market_product.discount_percent = discount_percent
            market_product.discount_price = None
        elif discount_price is not None:
            if discount_price >= market_product.market_price:
                raise ValueError(_('Discount price must be less than market price.'))
            market_product.discount_price = discount_price
            market_product.discount_percent = 0

        market_product.discount_start = start_date or timezone.now()
        market_product.discount_end = end_date

        market_product.save()

        logger.info(
            f"Discount applied to {market_product.slug}: "
            f"{discount_percent}% / {discount_price}"
        )

        return market_product

    @classmethod
    @db_transaction.atomic
    def remove_discount(cls, market_product):
        """حذف تخفیف"""
        market_product.discount_percent = 0
        market_product.discount_price = None
        market_product.discount_start = None
        market_product.discount_end = None
        market_product.save()

        logger.info(f"Discount removed from {market_product.slug}")

        return market_product

    @classmethod
    def increment_views(cls, market_product):
        """افزایش بازدید (بدون transaction - performance)"""
        MarketProduct.objects.filter(id=market_product.id).update(
            views_count=F('views_count') + 1
        )

    @classmethod
    @db_transaction.atomic
    def record_sale(cls, market_product, quantity=1):
        """
        ثبت فروش

        Args:
            market_product: محصول
            quantity: تعداد
        """
        market_product.sales_count += quantity
        market_product.available_quantity = max(0, market_product.available_quantity - quantity)

        if market_product.available_quantity <= 0:
            market_product.is_active = False

        market_product.save()

        logger.info(f"Sale recorded for {market_product.slug}: {quantity} units")

    # ==================== Search & Filter ====================

    @classmethod
    def search_products(cls, query=None, category_id=None, brand_id=None,
                        min_price=None, max_price=None, condition=None,
                        has_discount=None, in_stock=None,
                        sort_by=None, tags=None):
        """
        جستجوی پیشرفته محصولات

        Args:
            query: عبارت جستجو
            category_id: دسته‌بندی
            brand_id: برند
            min_price: حداقل قیمت
            max_price: حداکثر قیمت
            condition: وضعیت (نو/دسته دو)
            has_discount: فقط تخفیف‌دارها
            in_stock: فقط موجود
            sort_by: مرتب‌سازی
            tags: تگ‌ها

        Returns:
            QuerySet
        """
        queryset = MarketProduct.objects.filter(is_active=True).select_related(
            'stock_product__brand', 'stock_product__category'
        )

        # جستجوی متنی
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(short_description__icontains=query) |
                Q(full_description__icontains=query) |
                Q(tags__icontains=query) |
                Q(stock_product__name__icontains=query) |
                Q(stock_product__sku__icontains=query) |
                Q(stock_product__processor__icontains=query)
            )

        # فیلتر دسته‌بندی
        if category_id:
            queryset = queryset.filter(stock_product__category_id=category_id)

        # فیلتر برند
        if brand_id:
            queryset = queryset.filter(stock_product__brand_id=brand_id)

        # فیلتر قیمت
        if min_price is not None:
            queryset = queryset.filter(market_price__gte=min_price)

        if max_price is not None:
            queryset = queryset.filter(market_price__lte=max_price)

        # فیلتر وضعیت
        if condition:
            queryset = queryset.filter(stock_product__condition=condition)

        # فقط تخفیف‌دارها
        if has_discount:
            now = timezone.now()
            queryset = queryset.filter(
                Q(discount_percent__gt=0) |
                Q(discount_price__isnull=False, discount_start__lte=now, discount_end__gte=now)
            )

        # فقط موجود
        if in_stock:
            queryset = queryset.filter(available_quantity__gt=0)

        # فیلتر تگ
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag.strip())

        # مرتب‌سازی
        sort_options = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'price_asc': 'market_price',
            'price_desc': '-market_price',
            'rating': '-avg_rating',
            'popular': '-views_count',
            'bestseller': '-sales_count',
            'discount': '-discount_percent',
        }

        sort_field = sort_options.get(sort_by, '-created_at')
        queryset = queryset.order_by(sort_field)

        return queryset

    @classmethod
    def get_featured_products(cls, limit=10):
        """محصولات ویژه"""
        return MarketProduct.objects.filter(
            is_active=True, is_featured=True, available_quantity__gt=0
        ).order_by('-priority', '-avg_rating')[:limit]

    @classmethod
    def get_bestsellers(cls, limit=10):
        """پرفروش‌ترین‌ها"""
        return MarketProduct.objects.filter(
            is_active=True, sales_count__gt=0
        ).order_by('-sales_count')[:limit]

    @classmethod
    def get_new_arrivals(cls, limit=10):
        """جدیدترین‌ها"""
        return MarketProduct.objects.filter(
            is_active=True, available_quantity__gt=0
        ).order_by('-created_at')[:limit]

    @classmethod
    def get_related_products(cls, market_product, limit=6):
        """محصولات مرتبط"""
        return MarketProduct.objects.filter(
            is_active=True,
            stock_product__category=market_product.stock_product.category
        ).exclude(id=market_product.id).order_by('?')[:limit]

    @classmethod
    def get_price_range(cls, category_id=None, brand_id=None):
        """
        محدوده قیمت محصولات

        Returns:
            dict: {min, max}
        """
        queryset = MarketProduct.objects.filter(is_active=True)

        if category_id:
            queryset = queryset.filter(stock_product__category_id=category_id)

        if brand_id:
            queryset = queryset.filter(stock_product__brand_id=brand_id)

        result = queryset.aggregate(
            min_price=Min('market_price'),
            max_price=Max('market_price'),
        )

        return {
            'min': float(result['min_price'] or 0),
            'max': float(result['max_price'] or 0),
        }

    @classmethod
    def sync_all_stock_quantities(cls):
        """همگام‌سازی همه موجودی‌ها"""
        products = MarketProduct.objects.filter(is_active=True).select_related('stock_product')
        count = 0

        for product in products:
            try:
                cls.sync_stock_quantity(product)
                count += 1
            except Exception as e:
                logger.error(f"Sync failed for {product.slug}: {str(e)}")

        logger.info(f"Synced {count} market products with stock")
        return count

    @classmethod
    @db_transaction.atomic
    def bulk_update_prices(cls, category_id=None, brand_id=None, percent_change=None):
        """
        تغییر قیمت گروهی

        Args:
            category_id: دسته‌بندی
            brand_id: برند
            percent_change: درصد تغییر (+10 یا -5)

        Returns:
            int: تعداد محصولات بروزرسانی شده
        """
        queryset = MarketProduct.objects.filter(is_active=True)

        if category_id:
            queryset = queryset.filter(stock_product__category_id=category_id)

        if brand_id:
            queryset = queryset.filter(stock_product__brand_id=brand_id)

        if percent_change:
            factor = 1 + (percent_change / 100)
            count = queryset.update(
                market_price=F('market_price') * factor
            )

            logger.info(f"Bulk price update: {percent_change}% for {count} products")
            return count

        return 0