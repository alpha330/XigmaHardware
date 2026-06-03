from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.basket.models import Cart, CartItem
from decimal import Decimal


class CartItemSerializer(serializers.ModelSerializer):
    """سریالایزر آیتم سبد خرید"""
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    market_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_image',
            'quantity', 'unit_price', 'total_price',
            'is_active', 'is_available', 'market_available',
            'added_from_wishlist', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_image(self, obj):
        if obj.product.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.product.main_image.url)
            return obj.product.main_image.url
        return None

    def get_product_sku(self, obj):
        return obj.product.sku


class CartListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست سبدها"""
    total_items = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    can_checkout = serializers.BooleanField(read_only=True)
    cart_type_display = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'name', 'cart_type', 'cart_type_display',
            'status', 'total_items', 'total_quantity',
            'subtotal', 'discount_total', 'grand_total',
            'discount_percent', 'can_checkout',
            'created_at', 'updated_at',
        ]

    def get_cart_type_display(self, obj):
        return {
            'code': obj.cart_type,
            'label': obj.get_cart_type_display(),
            'icon': '🛒' if obj.is_cart else '⭐',
        }


class CartSerializer(serializers.ModelSerializer):
    """سریالایزر کامل سبد خرید"""
    items = serializers.SerializerMethodField()
    total_items = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    discount_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    can_checkout = serializers.BooleanField(read_only=True)
    cart_type_display = serializers.SerializerMethodField()
    discount_info = serializers.SerializerMethodField()
    converted_from_info = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'name', 'cart_type', 'cart_type_display',
            'status', 'notes',
            'items', 'total_items', 'total_quantity',
            'subtotal', 'discount_total', 'grand_total',
            'discount_percent', 'discount_amount', 'discount_type',
            'discount_info', 'discount_note',
            'can_checkout', 'converted_from_info',
            'converted_from', 'converted_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']

    def get_items(self, obj):
        items = obj.items.filter(is_active=True).select_related('product')
        return CartItemSerializer(items, many=True, context=self.context).data

    def get_cart_type_display(self, obj):
        return {
            'code': obj.cart_type,
            'label': obj.get_cart_type_display(),
            'icon': '🛒' if obj.is_cart else '⭐',
            'can_checkout': obj.can_checkout,
        }

    def get_discount_info(self, obj):
        if obj.discount_percent > 0 or obj.discount_amount > 0:
            return {
                'has_discount': True,
                'percent': float(obj.discount_percent) if obj.discount_percent > 0 else None,
                'amount': float(obj.discount_amount) if obj.discount_amount > 0 else None,
                'type': obj.discount_type,
                'set_by': obj.discount_set_by.get_display_name() if obj.discount_set_by else None,
                'note': obj.discount_note,
                'approved_at': obj.discount_approved_at,
            }
        return {'has_discount': False}

    def get_converted_from_info(self, obj):
        if obj.converted_from:
            return {
                'wishlist_id': str(obj.converted_from.id),
                'wishlist_name': obj.converted_from.name,
                'converted_at': obj.converted_at,
            }
        return None


class AddToCartSerializer(serializers.Serializer):
    """سریالایزر اضافه کردن به سبد"""
    product_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(default=1, min_value=1)
    cart_type = serializers.ChoiceField(
        choices=[('cart', 'Cart'), ('wishlist', 'Wishlist')],
        default='cart'
    )
    wishlist_name = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_product_id(self, value):
        from apps.stock.models import Product
        try:
            product = Product.objects.get(
                id=value,
                is_active=True,
                is_market_visible=True,
                market_status='published'
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(_('Product not available in market.'))

        if product.market_quantity < 1:
            raise serializers.ValidationError(_('Product is out of stock.'))

        self.context['product'] = product
        return value

    def validate_quantity(self, value):
        product = self.context.get('product')
        if product and value > product.market_quantity:
            raise serializers.ValidationError(
                _(f'Only {product.market_quantity} available in market.')
            )
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """سریالایزر بروزرسانی تعداد آیتم"""
    quantity = serializers.IntegerField(min_value=0, max_value=99)

    def validate_quantity(self, value):
        """اعتبارسنجی تعداد"""
        item = self.context.get('item')

        if item:
            # چک موجودی مارکت
            if value > item.product.market_quantity:
                raise serializers.ValidationError(
                    _(f'Only {item.product.market_quantity} available in market.')
                )

            # چک کن محصول هنوز توی مارکت هست
            if not item.product.is_market_visible or item.product.market_status != 'published':
                raise serializers.ValidationError(
                    _('This product is no longer available in market.')
                )

        return value

class WishlistDiscountSerializer(serializers.Serializer):
    """سریالایزر تنظیم تخفیف (فقط ادمین/مالی)"""
    discount_percent = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0'),
        max_value=Decimal('100'),
        required=False
    )
    discount_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0'),
        required=False
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500
    )

    def validate(self, data):
        """باید حداقل یکی از discount_percent یا discount_amount باشه"""
        percent = data.get('discount_percent')
        amount = data.get('discount_amount')

        if percent is None and amount is None:
            raise serializers.ValidationError(
                _('Either discount_percent or discount_amount is required.')
            )

        # نمی‌تونه هم درصد داشته باشه هم مبلغ
        if percent is not None and amount is not None:
            raise serializers.ValidationError(
                _('Provide either discount_percent OR discount_amount, not both.')
            )

        # اعتبارسنجی درصد
        if percent is not None:
            if percent < 0 or percent > 100:
                raise serializers.ValidationError({
                    'discount_percent': _('Must be between 0 and 100.')
                })

        # اعتبارسنجی مبلغ
        if amount is not None:
            wishlist = self.context.get('wishlist')
            if wishlist and hasattr(wishlist, 'cart'):
                if amount > wishlist.cart.subtotal:
                    raise serializers.ValidationError({
                        'discount_amount': _('Discount cannot exceed cart total.')
                    })

        return data


class ConvertWishlistSerializer(serializers.Serializer):
    """سریالایزر تبدیل Wishlist به Cart"""
    wishlist_id = serializers.UUIDField(required=True)

    def validate_wishlist_id(self, value):
        """اعتبارسنجی Wishlist"""
        from apps.basket.models import Cart
        from apps.basket.enums import CartType, CartStatus

        try:
            wishlist = Cart.objects.select_related('user').get(
                id=value,
                cart_type=CartType.WISHLIST,
                status=CartStatus.ACTIVE,
                user=self.context['request'].user
            )
        except Cart.DoesNotExist:
            raise serializers.ValidationError(_('Active wishlist not found.'))

        # چک کن آیتم داشته باشه
        if not wishlist.items.filter(is_active=True).exists():
            raise serializers.ValidationError(_('Wishlist is empty.'))

        # چک کن محصولات هنوز در مارکت موجود باشن
        unavailable_items = []
        for item in wishlist.items.filter(is_active=True):
            if not item.is_available:
                unavailable_items.append(item.product.name)

        if unavailable_items:
            raise serializers.ValidationError(
                _(f'Some products are no longer available: {", ".join(unavailable_items)}')
            )

        # چک کن سبد CART فعال دیگه‌ای در حالت checkout نباشه
        active_checkout = Cart.objects.filter(
            user=self.context['request'].user,
            cart_type=CartType.CART,
            status=CartStatus.CHECKOUT
        ).exists()

        if active_checkout:
            raise serializers.ValidationError(
                _('You have a cart in checkout. Please complete or cancel it first.')
            )

        self.context['wishlist'] = wishlist
        return value
