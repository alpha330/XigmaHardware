import logging
from decimal import Decimal
from django.db import models as db_models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.financial.models import Invoice, InvoiceItem
from apps.financial.serializers.invoice import (
    InvoiceSerializer,
    InvoiceListSerializer,
    InvoiceCreateSerializer,
    InvoiceItemCreateSerializer,
    InvoiceFromCartSerializer,
    WalletChargeSerializer,
    InvoiceStatusUpdateSerializer,
)
from apps.financial.permissions import CanManageFinancial, CanViewOwnInvoices
from apps.financial.services.invoice_service import InvoiceService

logger = logging.getLogger(__name__)


class InvoiceViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet مدیریت فاکتورها

    انواع فاکتور:
    - PROFORMA: پیش‌فاکتور
    - FINAL: فاکتور نهایی
    - WALLET_CHARGE: شارژ کیف پول
    - REFUND: فاکتور برگشتی
    """
    queryset = Invoice.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'create_from_cart':
            return InvoiceFromCartSerializer
        elif self.action == 'wallet_charge':
            return WalletChargeSerializer
        elif self.action == 'update_status':
            return InvoiceStatusUpdateSerializer
        elif self.action == 'add_item':
            return InvoiceItemCreateSerializer
        return InvoiceSerializer

    def get_permissions(self):
        # اکشن‌هایی که برای مشاهده نیاز است
        if self.action in ['list', 'retrieve', 'my_invoices']:
            return [IsAuthenticated(), CanViewOwnInvoices()]

        # اکشن‌هایی که کاربر برای خرید نیاز دارد
        elif self.action in ['create_from_cart', 'wallet_charge']:
            return [IsAuthenticated()]

        # اضافه کردن اکشن‌های آپدیت برای مالک فاکتور
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), CanViewOwnInvoices()] # فرض بر اینکه این پرمیشن چک می‌کند فاکتور مال خودشه

        return [IsAuthenticated(), CanManageFinancial()]

    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.select_related('user').prefetch_related('items', 'payments')

        # کاربران عادی فقط فاکتورهای خودشون
        if not user.is_superuser and user.role not in ['super_admin', 'accountant']:
            queryset = queryset.filter(user=user)

        # فیلترها
        invoice_type = self.request.query_params.get('type')
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # تاریخ (شمسی یا میلادی)
        from_date = self.request.query_params.get('from_date')
        if from_date:
            queryset = queryset.filter(created_at__date__gte=from_date)

        to_date = self.request.query_params.get('to_date')
        if to_date:
            queryset = queryset.filter(created_at__date__lte=to_date)

        # جستجو
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                db_models.Q(invoice_number__icontains=search) |
                db_models.Q(user__email__icontains=search) |
                db_models.Q(user__mobile__icontains=search) |
                db_models.Q(billing_company__icontains=search)
            )

        # فاکتورهای معوق
        overdue = self.request.query_params.get('overdue')
        if overdue:
            queryset = queryset.filter(
                status__in=['pending', 'partially_paid'],
                payment_due_date__lt=timezone.now().date()
            )

        return queryset

    def perform_create(self, serializer):
        """ایجاد فاکتور جدید"""
        data = serializer.validated_data
        user = data.get('user') or self.request.user

        invoice = InvoiceService.create_invoice(
            user=user,
            invoice_type=data.get('invoice_type', 'proforma'),
            items_data=data.get('items', []),
            discount_amount=data.get('discount_amount', 0),
            tax_percent=data.get('tax_percent', 9),
            shipping_amount=data.get('shipping_amount', 0),
            payment_due_date=data.get('payment_due_date'),
            notes=data.get('notes', ''),
            customer_notes=data.get('customer_notes', ''),
            billing_info={
                'name': data.get('billing_name', ''),
                'company': data.get('billing_company', ''),
                'national_id': data.get('billing_national_id', ''),
                'economic_code': data.get('billing_economic_code', ''),
                'address': data.get('billing_address', ''),
                'postal_code': data.get('billing_postal_code', ''),
                'phone': data.get('billing_phone', ''),
            },
            created_by=self.request.user,
        )

        logger.info(f"Invoice created: {invoice.invoice_number}")
        return invoice

    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """ایجاد فاکتور از سبد خرید"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = serializer.context['cart']
        payment_method = serializer.validated_data['payment_method']
        notes = serializer.validated_data.get('notes', '')

        try:
            invoice = InvoiceService.create_from_cart(
                cart=cart,
                payment_method=payment_method,
                notes=notes,
                created_by=request.user,
            )

            # اگر پرداخت با والت باشه، خودکار پرداخت کن
            if payment_method == 'wallet':
                transaction = InvoiceService.process_wallet_payment(
                    invoice=invoice,
                    user=cart.user,
                )

                return Response({
                    'message': _('Invoice created and paid from wallet.'),
                    'invoice': InvoiceSerializer(invoice, context={'request': request}).data,
                    'transaction': transaction.transaction_number,
                }, status=status.HTTP_201_CREATED)

            return Response({
                'message': _('Invoice created from cart.'),
                'invoice': InvoiceSerializer(invoice, context={'request': request}).data,
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def wallet_charge(self, request):
        """ایجاد فاکتور شارژ کیف پول"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.context['user']
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data['payment_method']
        description = serializer.validated_data.get('description', '')

        try:
            invoice = InvoiceService.create_wallet_charge(
                user=user,
                amount=amount,
                payment_method=payment_method,
                description=description,
                created_by=request.user,
            )

            logger.info(f"Wallet charge invoice created: {invoice.invoice_number}")

            return Response({
                'message': _('Wallet charge invoice created.'),
                'invoice': InvoiceSerializer(invoice, context={'request': request}).data,
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """افزودن آیتم به فاکتور"""
        invoice = self.get_object()

        if not invoice.is_proforma and invoice.status == 'draft':
            return Response(
                {'error': _('Only draft proforma invoices can be modified.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = InvoiceItem.objects.create(
            invoice=invoice,
            **serializer.validated_data
        )

        # محاسبه مجدد
        invoice.calculate_totals()

        return Response({
            'message': _('Item added.'),
            'item': InvoiceItemCreateSerializer(item).data,
            'invoice_total': float(invoice.total_amount),
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='remove-item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        """حذف آیتم از فاکتور"""
        invoice = self.get_object()

        if not invoice.is_proforma and invoice.status == 'draft':
            return Response(
                {'error': _('Only draft proforma invoices can be modified.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item = invoice.items.get(id=item_id)
            item.delete()
            invoice.calculate_totals()

            return Response({
                'message': _('Item removed.'),
                'invoice_total': float(invoice.total_amount),
            })
        except InvoiceItem.DoesNotExist:
            return Response({'error': _('Item not found.')}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def convert_to_final(self, request, pk=None):
        """تبدیل پیش‌فاکتور به فاکتور نهایی"""
        invoice = self.get_object()

        try:
            invoice = InvoiceService.convert_to_final(invoice)

            return Response({
                'message': _('Proforma converted to final invoice.'),
                'invoice': InvoiceSerializer(invoice, context={'request': request}).data,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """تغییر وضعیت فاکتور"""
        invoice = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'invoice': invoice}
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        reason = serializer.validated_data.get('reason', '')

        try:
            invoice = InvoiceService.update_invoice_status(
                invoice=invoice,
                status=new_status,
                reason=reason,
                updated_by=request.user,
            )

            return Response({
                'message': _('Status updated.'),
                'invoice': InvoiceListSerializer(invoice).data,
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """ثبت پرداخت برای فاکتور"""
        invoice = self.get_object()
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'card_to_card')
        reference_code = request.data.get('reference_code', '')

        try:
            amount = Decimal(str(amount))

            transaction = InvoiceService.record_payment(
                invoice=invoice,
                amount=amount,
                payment_method=payment_method,
                reference_code=reference_code,
                verified_by=request.user,
            )

            return Response({
                'message': _('Payment recorded.'),
                'transaction': transaction.transaction_number,
                'invoice_paid': float(invoice.paid_amount),
                'invoice_remaining': float(invoice.remaining_amount),
                'is_fully_paid': invoice.is_fully_paid,
            })
        except (ValueError, TypeError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """دانلود PDF فاکتور (نیاز به پیاده‌سازی)"""
        invoice = self.get_object()
        # TODO: Generate PDF
        return Response({'message': _('PDF generation coming soon.')})

    @action(detail=False, methods=['get'])
    def my_invoices(self, request):
        """فاکتورهای من (برای کاربران عادی)"""
        invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')

        page = self.paginate_queryset(invoices)
        if page is not None:
            serializer = InvoiceListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """فاکتورهای معوق"""
        invoices = Invoice.objects.filter(
            status__in=['pending', 'partially_paid'],
            payment_due_date__lt=timezone.now().date()
        ).order_by('payment_due_date')

        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار فاکتورها"""
        from django.db.models import Sum, Count

        invoices = Invoice.objects.all()

        # محدودیت کاربران عادی
        if not request.user.is_superuser and request.user.role not in ['super_admin', 'accountant']:
            invoices = invoices.filter(user=request.user)

        stats = {
            'total_invoices': invoices.count(),
            'total_amount': float(invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
            'total_paid': float(invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0),
            'by_type': {
                t: invoices.filter(invoice_type=t).count()
                for t in ['proforma', 'final', 'wallet_charge', 'refund']
            },
            'by_status': {
                s: invoices.filter(status=s).count()
                for s in ['draft', 'pending', 'paid', 'partially_paid', 'cancelled', 'overdue']
            },
            'overdue_count': invoices.filter(
                status__in=['pending', 'partially_paid'],
                payment_due_date__lt=timezone.now().date()
            ).count(),
            'this_month': {
                'count': invoices.filter(
                    created_at__month=timezone.now().month,
                    created_at__year=timezone.now().year
                ).count(),
                'amount': float(invoices.filter(
                    created_at__month=timezone.now().month,
                    created_at__year=timezone.now().year
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
            },
        }

        return Response(stats)