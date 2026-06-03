from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class AddToCartSerializer(serializers.Serializer):
    """سریالایزر اضافه کردن به سبد"""
    product_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(default=1, min_value=1)
    cart_type = serializers.ChoiceField(
        choices=[('cart', 'Cart'), ('wishlist', 'Wishlist')],
        default='cart'
    )
    wishlist_name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_product_id(self, value):
        """اعتبارسنجی محصول"""
        from apps.stock.models import Product

        try:
            product = Product.objects.select_related('brand', 'category').get(
                id=value,
                is_active=True,
                is_market_visible=True,
                market_status='published'
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(_('Product not available in market.'))

        # بررسی موجودی
        if product.market_quantity < 1:
            raise serializers.ValidationError(_('Product is out of stock in market.'))

        # ذخیره product برای استفاده در validate و create
        self.context['product'] = product
        return value

    def validate_quantity(self, value):
        """اعتبارسنجی تعداد"""
        product = self.context.get('product')

        if product and value > product.market_quantity:
            raise serializers.ValidationError(
                _(f'Only {product.market_quantity} available in market.')
            )

        # حداکثر ۹۹ عدد در هر سفارش
        if value > 99:
            raise serializers.ValidationError(_('Maximum 99 items per order.'))

        return value

    def validate_cart_type(self, value):
        """اعتبارسنجی نوع سبد"""
        user = self.context['request'].user

        # اگه wishlist انتخاب کرده، باید name هم بده
        if value == 'wishlist':
            wishlist_name = self.initial_data.get('wishlist_name', '').strip()
            if not wishlist_name:
                raise serializers.ValidationError(
                    _('Wishlist name is required when adding to wishlist.')
                )

        return value

    def validate(self, data):
        """اعتبارسنجی کلی"""
        # مطمئن شو product توی context هست
        if 'product' not in self.context:
            raise serializers.ValidationError({
                'product_id': _('Invalid product.')
            })

        # چک کن کاربر سبد فعال داره یا نه
        user = self.context['request'].user
        cart_type = data.get('cart_type')

        if cart_type == 'cart':
            from apps.basket.models import Cart
            from apps.basket.enums import CartStatus

            # چک کن سبد checkout نشده باشه
            active_cart = Cart.objects.filter(
                user=user,
                cart_type='cart',
                status='active'
            ).first()

            if active_cart and active_cart.status == 'checkout':
                raise serializers.ValidationError({
                    'cart_type': _('Your cart is currently in checkout. Please wait or contact support.')
                })

        return data
