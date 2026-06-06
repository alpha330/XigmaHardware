import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.market.models import MarketProduct
from apps.market.serializers.product import (
    MarketProductSerializer,
    MarketProductListSerializer,
    MarketProductCreateSerializer,
)
from apps.market.services.market_service import MarketService
from apps.market.services.rating_service import RatingService
from rest_framework import serializers

logger = logging.getLogger(__name__)


class MarketProductViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """
    ViewSet محصولات مارکت

    Actions عمومی:
    - list: لیست محصولات با فیلتر
    - retrieve: جزئیات محصول
    - search: جستجوی پیشرفته
    - featured: محصولات ویژه
    - bestsellers: پرفروش‌ها
    - new_arrivals: جدیدترین‌ها
    - related: محصولات مرتبط
    - price_range: محدوده قیمت

    Actions ادمین:
    - create: انتشار محصول جدید
    - update: ویرایش
    - apply_discount: اعمال تخفیف
    - remove_discount: حذف تخفیف
    - sync_stock: همگام‌سازی موجودی
    """
    queryset = MarketProduct.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return MarketProductListSerializer
        elif self.action == 'create':
            return MarketProductCreateSerializer
        return MarketProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search', 'featured',
                          'bestsellers', 'new_arrivals', 'related', 'price_range']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = MarketProduct.objects.filter(is_active=True).select_related(
            'stock_product__brand', 'stock_product__category'
        ).prefetch_related('media', 'ratings')

        # فیلترها
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(stock_product__category_id=category)

        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(stock_product__brand_id=brand)

        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(stock_product__condition=condition)

        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(market_price__gte=min_price)

        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(market_price__lte=max_price)

        in_stock = self.request.query_params.get('in_stock')
        if in_stock:
            queryset = queryset.filter(available_quantity__gt=0)

        has_discount = self.request.query_params.get('has_discount')
        if has_discount:
            queryset = queryset.filter(discount_percent__gt=0)

        # جستجو
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(tags__icontains=search) |
                Q(stock_product__name__icontains=search) |
                Q(stock_product__sku__icontains=search)
            )

        # مرتب‌سازی
        sort_by = self.request.query_params.get('sort', '-created_at')
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
        queryset = queryset.order_by(sort_options.get(sort_by, '-created_at'))

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """دریافت جزئیات + افزایش بازدید"""
        instance = self.get_object()
        MarketService.increment_views(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """ایجاد محصول در مارکت از Stock"""
        stock_product = serializer.validated_data['stock_product']
        market_data = {
            'title': serializer.validated_data.get('title', stock_product.name),
            'short_description': serializer.validated_data.get('short_description', ''),
            'full_description': serializer.validated_data.get('full_description', ''),
            'market_price': serializer.validated_data['market_price'],
            'discount_price': serializer.validated_data.get('discount_price'),
            'discount_percent': serializer.validated_data.get('discount_percent', 0),
            'discount_start': serializer.validated_data.get('discount_start'),
            'discount_end': serializer.validated_data.get('discount_end'),
            'min_order_quantity': serializer.validated_data.get('min_order_quantity', 1),
            'max_order_quantity': serializer.validated_data.get('max_order_quantity', 10),
            'tags': serializer.validated_data.get('tags', ''),
            'meta_title': serializer.validated_data.get('meta_title', ''),
            'meta_description': serializer.validated_data.get('meta_description', ''),
            'meta_keywords': serializer.validated_data.get('meta_keywords', ''),
            'is_active': serializer.validated_data.get('is_active', True),
            'is_featured': serializer.validated_data.get('is_featured', False),
        }

        try:
            market_product = MarketService.publish_to_market(stock_product, market_data)
            logger.info(f"Product published to market: {market_product.slug}")
            return market_product
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    @action(detail=False, methods=['get'])
    def search(self, request):
        """جستجوی پیشرفته"""
        products = MarketService.search_products(
            query=request.query_params.get('q'),
            category_id=request.query_params.get('category'),
            brand_id=request.query_params.get('brand'),
            min_price=request.query_params.get('min_price'),
            max_price=request.query_params.get('max_price'),
            condition=request.query_params.get('condition'),
            has_discount=request.query_params.get('has_discount'),
            in_stock=request.query_params.get('in_stock'),
            sort_by=request.query_params.get('sort'),
            tags=request.query_params.get('tags'),
        )

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = MarketProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = MarketProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """محصولات ویژه"""
        products = MarketService.get_featured_products(limit=20)
        serializer = MarketProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        """پرفروش‌ترین‌ها"""
        products = MarketService.get_bestsellers(limit=20)
        serializer = MarketProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """جدیدترین محصولات"""
        products = MarketService.get_new_arrivals(limit=20)
        serializer = MarketProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """محصولات مرتبط"""
        product = self.get_object()
        products = MarketService.get_related_products(product)
        serializer = MarketProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def price_range(self, request):
        """محدوده قیمت"""
        result = MarketService.get_price_range(
            category_id=request.query_params.get('category'),
            brand_id=request.query_params.get('brand'),
        )
        return Response(result)

    @action(detail=True, methods=['post'])
    def apply_discount(self, request, pk=None):
        """اعمال تخفیف"""
        product = self.get_object()

        discount_percent = request.data.get('discount_percent')
        discount_price = request.data.get('discount_price')

        try:
            product = MarketService.apply_discount(
                product,
                discount_percent=discount_percent,
                discount_price=discount_price,
                start_date=request.data.get('start_date'),
                end_date=request.data.get('end_date'),
            )

            return Response({
                'message': _('Discount applied.'),
                'final_price': float(product.final_price),
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_discount(self, request, pk=None):
        """حذف تخفیف"""
        product = self.get_object()
        MarketService.remove_discount(product)
        return Response({'message': _('Discount removed.')})

    @action(detail=True, methods=['post'])
    def sync_stock(self, request, pk=None):
        """همگام‌سازی موجودی با انبار"""
        product = self.get_object()
        MarketService.sync_stock_quantity(product)

        serializer = self.get_serializer(product)
        return Response({
            'message': _('Stock synced.'),
            'product': serializer.data,
        })

    @action(detail=True, methods=['get'])
    def rating_summary(self, request, pk=None):
        """خلاصه امتیازات"""
        product = self.get_object()
        summary = RatingService.get_rating_summary(product)
        return Response(summary)

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        """اضافه کردن به سبد خرید"""
        product = self.get_object()
        quantity = int(request.data.get('quantity', 1))

        if not product.is_in_stock:
            return Response({'error': _('Product out of stock.')}, status=status.HTTP_400_BAD_REQUEST)

        if quantity > product.available_quantity:
            return Response(
                {'error': _(f'Only {product.available_quantity} available.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ریدایرکت به Basket API
        from apps.basket.services.cart_service import CartService
        from apps.basket.enums import CartType

        cart = CartService.get_or_create_cart(request.user, CartType.CART)

        try:
            item, created = CartService.add_item(
                cart=cart,
                product=product.stock_product,
                quantity=quantity,
            )

            return Response({
                'message': _('Added to cart.'),
                'item_id': str(item.id),
                'cart_total': float(cart.grand_total),
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def compare(self, request):
        """مقایسه محصولات"""
        product_ids = request.query_params.get('ids', '').split(',')

        if not product_ids or len(product_ids) < 2:
            return Response(
                {'error': _('At least 2 product IDs required.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        products = MarketProduct.objects.filter(
            id__in=product_ids[:4],  # حداکثر ۴ محصول
            is_active=True
        ).select_related('stock_product__brand', 'stock_product__category')

        # ساخت جدول مقایسه
        compare_data = []
        for product in products:
            compare_data.append({
                'id': str(product.id),
                'title': product.title,
                'price': float(product.final_price),
                'rating': float(product.avg_rating),
                'brand': product.stock_product.brand.name if product.stock_product.brand else '-',
                'processor': product.stock_product.processor or '-',
                'ram': product.stock_product.ram or '-',
                'storage': product.stock_product.total_storage or '-',
                'form_factor': product.stock_product.form_factor or '-',
                'in_stock': product.is_in_stock,
            })

        return Response(compare_data)