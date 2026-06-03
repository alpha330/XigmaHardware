from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.basket.models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    """سریالایزر Wishlist"""
    total_items = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    estimated_total = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    budget_remaining = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    cart = serializers.SerializerMethodField()
    discount_info = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'name', 'description',
            'is_active', 'is_public', 'can_convert',
            'budget_limit', 'target_date',
            'total_items', 'total_quantity',
            'subtotal', 'estimated_total',
            'is_over_budget', 'budget_remaining',
            'discount_info', 'cart',
            'conversion_count', 'converted_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'conversion_count', 'created_at', 'updated_at']

    def get_cart(self, obj):
        """اطلاعات Cart متصل به Wishlist"""
        if hasattr(obj, 'cart'):
            from apps.basket.serializers.cart import CartSerializer
            return CartSerializer(obj.cart, context=self.context).data
        return None

    def get_discount_info(self, obj):
        if hasattr(obj, 'cart') and obj.cart and (obj.cart.discount_percent > 0 or obj.cart.discount_amount > 0):
            return {
                'has_discount': True,
                'percent': float(obj.cart.discount_percent),
                'amount': float(obj.cart.discount_amount),
                'type': obj.cart.discount_type,
                'set_by': obj.cart.discount_set_by.get_display_name() if obj.cart.discount_set_by else None,
                'note': obj.cart.discount_note,
                'approved_at': obj.cart.discount_approved_at,
            }
        return {'has_discount': False}


class WishlistCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد Wishlist"""

    class Meta:
        model = Wishlist
        fields = [
            'name', 'description', 'budget_limit',
            'target_date', 'is_public',
        ]

    def validate_name(self, value):
        user = self.context['request'].user
        if Wishlist.objects.filter(user=user, name=value, is_active=True).exists():
            raise serializers.ValidationError(
                _('You already have a wishlist with this name.')
            )
        return value


class WishlistConvertSerializer(serializers.Serializer):
    """سریالایزر تبدیل Wishlist به Cart"""
    wishlist_id = serializers.UUIDField(required=True)

    def validate_wishlist_id(self, value):
        try:
            wishlist = Wishlist.objects.get(
                id=value,
                user=self.context['request'].user,
                is_active=True,
                can_convert=True,
            )
        except Wishlist.DoesNotExist:
            raise serializers.ValidationError(
                _('Wishlist not found or cannot be converted.')
            )

        self.context['wishlist'] = wishlist
        return value
