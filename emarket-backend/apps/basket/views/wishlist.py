import logging
from django.db import models as db_models
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.basket.models import Wishlist, Cart, CartItem
from apps.basket.enums import CartType, CartStatus
from apps.basket.serializers.wishlist import (
    WishlistSerializer,
    WishlistCreateSerializer,
    WishlistConvertSerializer,
)
from apps.basket.serializers.cart import (
    AddToCartSerializer,
    UpdateCartItemSerializer,
    CartSerializer,
    CartItemSerializer,
    WishlistDiscountSerializer,
)
from apps.basket.permissions import IsCartOwner, CanSetDiscount
from apps.basket.services.wishlist_service import WishlistService
from apps.basket.services.cart_service import CartService

from apps.basket.permissions import (
    IsCartOwner, CanSetDiscount, IsWishlistOwner,
    IsWishlistActive, CanConvertWishlist, CanAddToCart,
    CanUpdateCartItem, CanClearCart, IsNotInCheckout,
    CanViewWishlistDiscount,
)

logger = logging.getLogger(__name__)


class WishlistViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet مدیریت سبد آرزوها

    Actions:
    - list: لیست Wishlist های کاربر
    - create: ایجاد Wishlist جدید
    - retrieve: جزئیات Wishlist
    - update/partial_update: ویرایش Wishlist
    - destroy: حذف Wishlist
    - add_item: اضافه کردن محصول
    - update_item: تغییر تعداد
    - remove_item: حذف آیتم
    - remove_selected: حذف گروهی
    - clear: خالی کردن
    - convert_to_cart: تبدیل به سبد خرید
    - duplicate: کپی کردن
    - set_discount: تنظیم تخفیف (ادمین)
    - budget_analysis: تحلیل بودجه
    - active: لیست فعال‌ها
    """
    queryset = Wishlist.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return WishlistCreateSerializer
        elif self.action == 'add_item':
            return AddToCartSerializer
        elif self.action == 'update_item':
            return UpdateCartItemSerializer
        elif self.action == 'set_discount':
            return WishlistDiscountSerializer
        elif self.action == 'convert_to_cart':
            return WishlistConvertSerializer
        return WishlistSerializer

    def get_permissions(self):
        """
        تنظیم permissions بر اساس action
        """
        permission_map = {
            'list': [IsAuthenticated()],
            'create': [IsAuthenticated(), CanAddToCart()],
            'retrieve': [IsAuthenticated(), IsWishlistOwner()],
            'update': [IsAuthenticated(), IsWishlistOwner(), IsWishlistActive()],
            'partial_update': [IsAuthenticated(), IsWishlistOwner(), IsWishlistActive()],
            'destroy': [IsAuthenticated(), IsWishlistOwner()],
            'add_item': [IsAuthenticated(), IsWishlistOwner(), IsWishlistActive()],
            'update_item': [IsAuthenticated(), IsWishlistOwner(), IsWishlistActive(), CanUpdateCartItem()],
            'remove_item': [IsAuthenticated(), IsWishlistOwner(), IsNotInCheckout()],
            'remove_selected': [IsAuthenticated(), IsWishlistOwner(), IsNotInCheckout()],
            'clear': [IsAuthenticated(), IsWishlistOwner(), CanClearCart()],
            'convert_to_cart': [IsAuthenticated(), IsWishlistOwner(), CanConvertWishlist()],
            'duplicate': [IsAuthenticated(), IsWishlistOwner()],
            'set_discount': [IsAuthenticated(), CanSetDiscount(), CanViewWishlistDiscount()],
            'clear_discount': [IsAuthenticated(), CanSetDiscount()],
            'budget_analysis': [IsAuthenticated(), IsWishlistOwner()],
            'items': [IsAuthenticated(), IsWishlistOwner()],
            'active': [IsAuthenticated()],
            'summary': [IsAuthenticated()],
        }

        return permission_map.get(self.action, [IsAuthenticated()])

    def get_queryset(self):
        """فقط Wishlist های کاربر جاری"""
        return Wishlist.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related('cart__items__product')

    def perform_create(self, serializer):
        """ایجاد Wishlist + Cart متصل"""
        wishlist = serializer.save(user=self.request.user)

        # ایجاد Cart از نوع WISHLIST متصل به Wishlist
        Cart.objects.create(
            user=self.request.user,
            cart_type=CartType.WISHLIST,
            status=CartStatus.ACTIVE,
            name=wishlist.name,
        )

        logger.info(f"Wishlist created: {wishlist.name}")
        return wishlist

    def perform_destroy(self, instance):
        """حذف نرم (غیرفعال‌سازی)"""
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])

        # غیرفعال کردن Cart متصل
        if hasattr(instance, 'cart'):
            instance.cart.status = CartStatus.ABANDONED
            instance.cart.save(update_fields=['status'])

        logger.info(f"Wishlist deleted: {instance.name}")

    # ==================== Custom Actions ====================

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """اضافه کردن محصول به Wishlist"""
        wishlist = self.get_object()

        # Cart متصل به Wishlist
        if not hasattr(wishlist, 'cart'):
            # ایجاد Cart اگر وجود نداشت
            cart = Cart.objects.create(
                user=request.user,
                cart_type=CartType.WISHLIST,
                status=CartStatus.ACTIVE,
                name=wishlist.name,
            )
        else:
            cart = wishlist.cart

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        product = serializer.context['product']
        quantity = serializer.validated_data['quantity']
        notes = serializer.validated_data.get('notes', '')

        try:
            item, created = CartService.add_item(cart, product, quantity, notes)

            return Response({
                'message': _('Product added to wishlist.'),
                'item': CartItemSerializer(item, context={'request': request}).data,
                'wishlist_summary': {
                    'total_items': cart.total_items,
                    'total_quantity': cart.total_quantity,
                    'subtotal': float(cart.subtotal),
                    'estimated_total': float(cart.grand_total),
                }
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='update-item/(?P<item_id>[^/.]+)')
    def update_item(self, request, pk=None, item_id=None):
        """بروزرسانی تعداد آیتم در Wishlist"""
        wishlist = self.get_object()

        if not hasattr(wishlist, 'cart'):
            return Response({'error': _('Wishlist has no items.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = wishlist.cart.items.get(id=item_id, is_active=True)
        except CartItem.DoesNotExist:
            return Response({'error': _('Item not found.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data, context={'item': item})
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']

        try:
            if quantity == 0:
                CartService.remove_item(item)
                return Response({'message': _('Item removed from wishlist.')})

            item = CartService.update_quantity(item, quantity)

            return Response({
                'message': _('Quantity updated.'),
                'item': CartItemSerializer(item, context={'request': request}).data,
                'wishlist_summary': {
                    'subtotal': float(wishlist.cart.subtotal),
                    'estimated_total': float(wishlist.cart.grand_total),
                }
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        """حذف آیتم از Wishlist"""
        wishlist = self.get_object()

        if not hasattr(wishlist, 'cart'):
            return Response({'error': _('Wishlist has no items.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = wishlist.cart.items.get(id=item_id, is_active=True)
        except CartItem.DoesNotExist:
            return Response({'error': _('Item not found.')}, status=status.HTTP_404_NOT_FOUND)

        CartService.remove_item(item)

        return Response({
            'message': _('Item removed from wishlist.'),
            'wishlist_summary': {
                'total_items': wishlist.cart.total_items,
                'subtotal': float(wishlist.cart.subtotal),
            }
        })

    @action(detail=True, methods=['post'])
    def remove_selected(self, request, pk=None):
        """حذف گروهی آیتم‌ها از Wishlist"""
        wishlist = self.get_object()

        if not hasattr(wishlist, 'cart'):
            return Response({'error': _('Wishlist has no items.')}, status=status.HTTP_404_NOT_FOUND)

        item_ids = request.data.get('item_ids', [])

        if not item_ids:
            return Response({'error': _('No items selected.')}, status=status.HTTP_400_BAD_REQUEST)

        count = CartService.remove_items(wishlist.cart, item_ids)

        return Response({
            'message': _(f'{count} item(s) removed.'),
            'removed_count': count,
        })

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """خالی کردن کل Wishlist"""
        wishlist = self.get_object()

        if not hasattr(wishlist, 'cart'):
            return Response({'error': _('Wishlist has no items.')}, status=status.HTTP_404_NOT_FOUND)

        count = CartService.clear_cart(wishlist.cart)

        return Response({
            'message': _(f'Wishlist cleared. {count} item(s) removed.'),
        })

    @action(detail=True, methods=['post'])
    def convert_to_cart(self, request, pk=None):
        """تبدیل Wishlist به سبد خرید واقعی"""
        wishlist = self.get_object()

        if not wishlist.is_active:
            return Response({'error': _('Wishlist is not active.')}, status=status.HTTP_400_BAD_REQUEST)

        if not wishlist.can_convert:
            return Response(
                {'error': _('Conversion is blocked. Contact support.')},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            cart = WishlistService.convert_to_cart(wishlist)

            return Response({
                'message': _('Wishlist converted to cart!'),
                'discount_applied': cart.discount_percent > 0 or cart.discount_amount > 0,
                'discount_percent': float(cart.discount_percent) if cart.discount_percent > 0 else None,
                'estimated_total': float(cart.grand_total),
                'cart': CartSerializer(cart, context={'request': request}).data,
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """کپی کردن Wishlist"""
        wishlist = self.get_object()

        new_wishlist = WishlistService.duplicate_wishlist(wishlist)

        return Response({
            'message': _('Wishlist duplicated.'),
            'wishlist': WishlistSerializer(new_wishlist, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def set_discount(self, request, pk=None):
        """تنظیم تخفیف (فقط ادمین/مالی)"""
        wishlist = self.get_object()

        if not hasattr(wishlist, 'cart'):
            return Response({'error': _('Wishlist has no cart.' )}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(
            data=request.data,
            context={'wishlist': wishlist}
        )
        serializer.is_valid(raise_exception=True)

        try:
            cart = CartService.apply_discount(
                cart=wishlist.cart,
                percent=serializer.validated_data.get('discount_percent'),
                amount=serializer.validated_data.get('discount_amount'),
                set_by=request.user,
                note=serializer.validated_data.get('note', ''),
            )

            return Response({
                'message': _('Discount applied to wishlist.'),
                'discount_percent': float(cart.discount_percent),
                'discount_amount': float(cart.discount_amount),
                'subtotal': float(cart.subtotal),
                'discount_total': float(cart.discount_total),
                'grand_total': float(cart.grand_total),
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def clear_discount(self, request, pk=None):
        """حذف تخفیف"""
        wishlist = self.get_object()

        if not hasattr(wishlist, 'cart'):
            return Response({'error': _('Wishlist has no cart.')}, status=status.HTTP_400_BAD_REQUEST)

        CartService.remove_discount(wishlist.cart)

        return Response({'message': _('Discount removed.')})

    @action(detail=True, methods=['get'])
    def budget_analysis(self, request, pk=None):
        """تحلیل بودجه Wishlist"""
        wishlist = self.get_object()

        analysis = WishlistService.get_budget_analysis(wishlist)

        return Response(analysis)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """لیست آیتم‌های Wishlist"""
        wishlist = self.get_object()

        if not hasattr(wishlist, 'cart'):
            return Response([])

        items = wishlist.cart.items.filter(is_active=True).select_related('product')

        page = self.paginate_queryset(items)
        if page is not None:
            serializer = CartItemSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = CartItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """لیست Wishlist های فعال"""
        wishlists = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(wishlists, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """خلاصه همه Wishlist های کاربر"""
        summary = WishlistService.get_user_wishlists_summary(request.user)
        return Response(summary)
