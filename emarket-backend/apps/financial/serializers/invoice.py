from decimal import Decimal
from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.financial.models import Invoice, InvoiceItem
from apps.accounts.serializers.user import UserListSerializer
from apps.financial.enums import InvoiceType, InvoiceStatus


class InvoiceItemSerializer(serializers.ModelSerializer):
    """سریالایزر اقلام فاکتور"""
    total_price = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    product_name = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'product', 'product_name', 'description', 'sku',
            'quantity', 'unit_price', 'discount_percent', 'tax_percent',
            'total_price', 'warranty_description', 'notes',
        ]
        read_only_fields = ['id', 'total_price']

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.name
        return None


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد اقلام فاکتور"""

    class Meta:
        model = InvoiceItem
        fields = [
            'product', 'description', 'sku',
            'quantity', 'unit_price', 'discount_percent',
            'tax_percent', 'warranty_description', 'notes',
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(_('Quantity must be at least 1.'))
        if value > 999:
            raise serializers.ValidationError(_('Maximum quantity is 999.'))
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Price cannot be negative.'))
        return value

    def validate_discount_percent(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError(_('Discount must be between 0 and 100.'))
        return value


class InvoiceListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست فاکتورها"""
    user_name = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(read_only=True)
    type_badge = serializers.SerializerMethodField()
    status_badge = serializers.SerializerMethodField()
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_overdue = serializers.SerializerMethodField()
    created_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'type_badge',
            'status', 'status_badge', 'user_name', 'items_count',
            'total_amount', 'paid_amount', 'balance',
            'payment_method', 'payment_due_date',
            'is_overdue', 'created_at_jalali', 'paid_at',
        ]

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_display_name()
        return 'N/A'

    def get_type_badge(self, obj):
        icons = {
            'proforma': '📄',
            'final': '✅',
            'wallet_charge': '💰',
            'refund': '↩️',
        }
        return {
            'code': obj.invoice_type,
            'label': obj.get_invoice_type_display(),
            'icon': icons.get(obj.invoice_type, '📄'),
        }

    def get_status_badge(self, obj):
        colors = {
            'draft': 'secondary',
            'pending': 'warning',
            'paid': 'success',
            'partially_paid': 'info',
            'cancelled': 'danger',
            'expired': 'dark',
            'refunded': 'primary',
        }
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
            'color': colors.get(obj.status, 'secondary'),
        }

    def get_is_overdue(self, obj):
        if obj.payment_due_date and obj.status in ['pending', 'partially_paid']:
            return obj.payment_due_date < timezone.now().date()
        return False

    def get_created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')


class InvoiceSerializer(serializers.ModelSerializer):
    """سریالایزر کامل فاکتور"""
    user = UserListSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = serializers.SerializerMethodField()
    type_badge = serializers.SerializerMethodField()
    status_badge = serializers.SerializerMethodField()
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    payments_count = serializers.IntegerField(read_only=True)
    is_overdue = serializers.SerializerMethodField()
    created_at_jalali = serializers.SerializerMethodField()
    paid_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'type_badge',
            'status', 'status_badge', 'user',
            'cart', 'related_invoice',
            'items', 'items_count', 'payments', 'payments_count',
            'subtotal', 'discount_amount', 'tax_amount',
            'shipping_amount', 'total_amount',
            'paid_amount', 'balance', 'remaining_amount',
            'currency', 'payment_method', 'payment_due_date',
            'paid_at', 'paid_at_jalali', 'is_overdue',
            'billing_name', 'billing_company', 'billing_national_id',
            'billing_economic_code', 'billing_address',
            'billing_postal_code', 'billing_phone',
            'notes', 'customer_notes',
            'created_by', 'approved_by', 'approved_at',
            'created_at', 'created_at_jalali', 'updated_at', 'expires_at',
        ]
        read_only_fields = [
            'id', 'invoice_number', 'created_at', 'updated_at',
            'paid_at', 'approved_at', 'items_count', 'payments_count',
        ]

    def get_payments(self, obj):
        from .transaction import TransactionListSerializer
        payments = obj.payments.all()[:20]
        return TransactionListSerializer(payments, many=True).data

    def get_type_badge(self, obj):
        return {
            'code': obj.invoice_type,
            'label': obj.get_invoice_type_display(),
        }

    def get_status_badge(self, obj):
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
        }

    def get_is_overdue(self, obj):
        if obj.payment_due_date and obj.status in ['pending', 'partially_paid']:
            return obj.payment_due_date < timezone.now().date()
        return False

    def get_created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return None

    def get_paid_at_jalali(self, obj):
        if obj.paid_at:
            try:
                import jdatetime
                return jdatetime.datetime.fromgregorian(datetime=obj.paid_at).strftime('%Y/%m/%d %H:%M')
            except ImportError:
                return None
        return None


class InvoiceCreateSerializer(serializers.Serializer):
    """سریالایزر ایجاد فاکتور دستی"""
    user_id = serializers.UUIDField(required=True)
    invoice_type = serializers.ChoiceField(
        choices=[('proforma', 'Proforma'), ('final', 'Final')],
        default='proforma'
    )
    items = InvoiceItemCreateSerializer(many=True, required=True)
    discount_amount = serializers.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_percent = serializers.DecimalField(max_digits=5, decimal_places=2, default=9)
    shipping_amount = serializers.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_due_date = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    customer_notes = serializers.CharField(required=False, allow_blank=True, max_length=1000)

    # Billing
    billing_name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    billing_company = serializers.CharField(required=False, allow_blank=True, max_length=200)
    billing_national_id = serializers.CharField(required=False, allow_blank=True, max_length=11)
    billing_economic_code = serializers.CharField(required=False, allow_blank=True, max_length=12)
    billing_address = serializers.CharField(required=False, allow_blank=True)
    billing_postal_code = serializers.CharField(required=False, allow_blank=True, max_length=10)
    billing_phone = serializers.CharField(required=False, allow_blank=True, max_length=15)

    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError(_('At least one item is required.'))
        return value

    def validate_discount_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(_('Discount cannot be negative.'))
        return value

    def validate_user_id(self, value):
        from apps.accounts.models import User
        try:
            user = User.objects.get(id=value, is_active=True)
            self.context['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(_('User not found.'))
        return value


class InvoiceFromCartSerializer(serializers.Serializer):
    """سریالایزر ایجاد فاکتور از Cart"""
    cart_id = serializers.UUIDField(required=True)
    payment_method = serializers.ChoiceField(
        choices=[('wallet', 'Wallet'), ('online_gateway', 'Online Gateway'),
                 ('card_to_card', 'Card to Card'), ('bank_transfer', 'Bank Transfer')],
        default='wallet'
    )
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_cart_id(self, value):
        from apps.basket.models import Cart
        from apps.basket.enums import CartType, CartStatus

        try:
            cart = Cart.objects.get(
                id=value,
                cart_type=CartType.CART,
                status__in=[CartStatus.ACTIVE, CartStatus.CHECKOUT]
            )
        except Cart.DoesNotExist:
            raise serializers.ValidationError(_('Active cart not found.'))

        if not cart.items.filter(is_active=True).exists():
            raise serializers.ValidationError(_('Cart is empty.'))

        self.context['cart'] = cart
        return value


class WalletChargeSerializer(serializers.Serializer):
    """سریالایزر شارژ کیف پول"""
    user_id = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('1000'))
    payment_method = serializers.ChoiceField(
        choices=[('card_to_card', 'Card to Card'), ('bank_transfer', 'Bank Transfer'),
                 ('online_gateway', 'Online Gateway')],
        default='online_gateway'
    )
    description = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_user_id(self, value):
        from apps.accounts.models import User
        try:
            user = User.objects.get(id=value, is_active=True)
            self.context['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(_('User not found.'))
        return value

    def validate_amount(self, value):
        if value < 1000:
            raise serializers.ValidationError(_('Minimum charge amount is 1,000 Rials.'))
        if value > 1000000000:
            raise serializers.ValidationError(_('Maximum charge amount is 1,000,000,000 Rials.'))
        return value


class InvoiceStatusUpdateSerializer(serializers.Serializer):
    """سریالایزر تغییر وضعیت فاکتور"""
    status = serializers.ChoiceField(choices=InvoiceStatus.choices)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_status(self, value):
        invoice = self.context.get('invoice')
        if invoice:
            # اعتبارسنجی تغییر وضعیت
            valid_transitions = {
                'draft': ['pending', 'cancelled'],
                'pending': ['paid', 'cancelled', 'expired'],
                'partially_paid': ['paid', 'cancelled'],
                'paid': ['refunded'],
            }

            current = invoice.status
            if current in valid_transitions and value not in valid_transitions[current]:
                raise serializers.ValidationError(
                    _(f'Cannot change from {current} to {value}.')
                )

        return value