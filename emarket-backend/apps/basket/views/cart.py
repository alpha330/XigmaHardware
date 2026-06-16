import logging
from django.db import models as db_models
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.basket.models import Cart, CartItem
from apps.basket.enums import CartType, CartStatus
from apps.basket.serializers.cart import (
    CartSerializer, CartListSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer,
    WishlistDiscountSerializer, ConvertWishlistSerializer,
)
from apps.basket.permissions import (
    IsCartOwner, CanSetDiscount, IsCartActive,
    CanAddToCart, CanCheckout, CanUpdateCartItem,
    CanClearCart, IsNotInCheckout,
)

logger = logging.getLogger(__name__)


class CartViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    ViewSet مدیریت سبد خرید

    Actions:
    - my_cart: سبد خرید فعال کاربر
    - my_wishlists: سبدهای آرزو
    - add_item: اضافه کردن محصول
    - update_item: تغییر تعداد
    - remove_item: حذف آیتم
    - clear_cart: خالی کردن سبد
    - convert_to_cart: تبدیل آرزو به سبد
    - set_discount: تنظیم تخفیف (ادمین)
    """

    queryset = Cart.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'my_wishlists']:
            return CartListSerializer
        elif self.action == 'add_item':
            return AddToCartSerializer
        elif self.action == 'update_item':
            return UpdateCartItemSerializer
        elif self.action == 'set_discount':
            return WishlistDiscountSerializer
        elif self.action == 'convert_to_cart':
            return ConvertWishlistSerializer
        return CartSerializer

    def get_permissions(self):
        """
        تنظیم permissions بر اساس action
        """
        permission_map = {
            'list': [IsAuthenticated()],
            'retrieve': [IsAuthenticated(), IsCartOwner()],
            'my_cart': [IsAuthenticated()],
            'my_wishlists': [IsAuthenticated()],
            'add_item': [IsAuthenticated(), CanAddToCart()],
            'update_item': [IsAuthenticated(), IsCartOwner(), IsCartActive(), CanUpdateCartItem()],
            'remove_item': [IsAuthenticated(), IsCartOwner(), IsNotInCheckout()],
            'remove_selected': [IsAuthenticated(), IsCartOwner(), IsNotInCheckout()],
            'clear_cart': [IsAuthenticated(), IsCartOwner(), CanClearCart()],
            'convert_to_cart': [IsAuthenticated(), IsCartOwner(), IsCartActive()],
            'set_discount': [IsAuthenticated(), CanSetDiscount()],
            'clear_discount': [IsAuthenticated(), CanSetDiscount()],
            'summary': [IsAuthenticated(), IsCartOwner()],
        }

        return permission_map.get(self.action, [IsAuthenticated()])

    def get_queryset(self):
        return Cart.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product')

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """دریافت سبد خرید فعال"""
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            cart_type=CartType.CART,
            status=CartStatus.ACTIVE,
            defaults={'name': 'My Cart'}
        )
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_wishlists(self, request):
        """لیست سبدهای آرزو"""
        wishlists = Cart.objects.filter(
            user=request.user,
            cart_type=CartType.WISHLIST,
            status=CartStatus.ACTIVE
        )
        serializer = CartListSerializer(wishlists, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """اضافه کردن محصول به سبد"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.context['product']
        cart_type = serializer.validated_data['cart_type']
        quantity = serializer.validated_data['quantity']

        # 🎯 تغییر نام _ به cart_created برای جلوگیری از تداخل با تابع ترجمه جنگو
        if cart_type == 'cart':
            cart, cart_created = Cart.objects.get_or_create(
                user=request.user,
                cart_type=CartType.CART,
                status=CartStatus.ACTIVE,
                defaults={'name': 'My Cart'}
            )
        else:
            wishlist_name = serializer.validated_data.get('wishlist_name', 'My Wishlist')
            cart, cart_created = Cart.objects.get_or_create(
                user=request.user,
                cart_type=CartType.WISHLIST,
                status=CartStatus.ACTIVE,
                name=wishlist_name,
                defaults={'name': wishlist_name}
            )

        # اضافه کردن یا بروزرسانی آیتم
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': product.final_market_price,
                'notes': serializer.validated_data.get('notes', ''),
                'is_active': True,
            }
        )

        if not created:
            if not item.is_active:
                item.is_active = True
                item.quantity = quantity
            else:
                item.quantity += quantity
            item.unit_price = product.final_market_price  # آپدیت قیمت
            item.save()

        logger.info(f"Added to {cart_type}: {product.sku} x{quantity}")

        return Response({
            'message': _('Product added to {}.'.format(
                'cart' if cart_type == 'cart' else 'wishlist'
            )),
            'item': CartItemSerializer(item, context={'request': request}).data,
            'cart_summary': {
                'total_items': cart.total_items,
                'total_quantity': cart.total_quantity,
                'subtotal': float(cart.subtotal),
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='update-item/(?P<item_id>[^/.]+)')
    def update_item(self, request, pk=None, item_id=None):
        """بروزرسانی تعداد آیتم"""
        cart = self.get_object()

        try:
            item = cart.items.get(id=item_id, is_active=True)
        except CartItem.DoesNotExist:
            return Response({'error': _('Item not found.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data, context={'item': item})
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']

        if quantity == 0:
            item.remove()
            return Response({'message': _('Item removed.')})
        else:
            item.update_quantity(quantity)

        return Response({
            'message': _('Quantity updated.'),
            'item': CartItemSerializer(item, context={'request': request}).data,
        })

    @action(detail=True, methods=['post'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        """حذف آیتم از سبد"""
        cart = self.get_object()

        try:
            item = cart.items.get(id=item_id, is_active=True)
        except CartItem.DoesNotExist:
            return Response({'error': _('Item not found.')}, status=status.HTTP_404_NOT_FOUND)

        item.remove()

        return Response({'message': _('Item removed from cart.')})

    @action(detail=True, methods=['post'])
    def remove_selected(self, request, pk=None):
        """حذف گروهی آیتم‌ها"""
        cart = self.get_object()
        item_ids = request.data.get('item_ids', [])

        if not item_ids:
            return Response({'error': _('No items selected.')}, status=status.HTTP_400_BAD_REQUEST)

        updated = cart.items.filter(id__in=item_ids, is_active=True).update(is_active=False)

        return Response({
            'message': _(f'{updated} item(s) removed.'),
            'removed_count': updated,
        })

    @action(detail=True, methods=['post'])
    def clear_cart(self, request, pk=None):
        """خالی کردن کل سبد"""
        cart = self.get_object()
        count = cart.items.filter(is_active=True).update(is_active=False)

        return Response({
            'message': _(f'Cart cleared. {count} item(s) removed.'),
        })

    @action(detail=True, methods=['post'])
    def convert_to_cart(self, request, pk=None):
        """تبدیل Wishlist به Cart"""
        wishlist = self.get_object()

        if not wishlist.is_wishlist:
            return Response({'error': _('Only wishlist can be converted.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = wishlist.convert_to_cart()
            logger.info(f"Wishlist {wishlist.id} converted to Cart {cart.id}")

            return Response({
                'message': _('Wishlist converted to cart successfully.'),
                'cart': CartSerializer(cart, context={'request': request}).data,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def set_discount(self, request, pk=None):
        """تنظیم تخفیف (فقط ادمین/مالی)"""
        cart = self.get_object()

        if not cart.is_wishlist:
            return Response({'error': _('Discount can only be set on wishlist.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart.set_discount(
                percent=serializer.validated_data.get('discount_percent'),
                amount=serializer.validated_data.get('discount_amount'),
                set_by=request.user,
                note=serializer.validated_data.get('note', ''),
            )

            return Response({
                'message': _('Discount applied.'),
                'cart': CartSerializer(cart, context={'request': request}).data,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def clear_discount(self, request, pk=None):
        """حذف تخفیف"""
        cart = self.get_object()
        cart.clear_discount()

        return Response({'message': _('Discount removed.')})

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """خلاصه سبد خرید"""
        cart = self.get_object()

        return Response({
            'total_items': cart.total_items,
            'total_quantity': cart.total_quantity,
            'subtotal': float(cart.subtotal),
            'discount_total': float(cart.discount_total),
            'grand_total': float(cart.grand_total),
            'has_discount': cart.discount_percent > 0 or cart.discount_amount > 0,
            'discount_percent': float(cart.discount_percent),
            'can_checkout': cart.can_checkout,
            'items_available': cart.items.filter(is_active=True).count(),
            'items_unavailable': cart.items.filter(is_active=True).exclude(
                db_models.Q(product__is_market_visible=True) &
                db_models.Q(product__market_status='published')
            ).count(),
        })
