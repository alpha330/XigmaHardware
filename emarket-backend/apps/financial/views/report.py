import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.financial.models import FinancialReport
from apps.financial.serializers.report import (
    ReportSerializer,
    ReportGenerateSerializer,
)
from apps.financial.permissions import CanManageFinancial
from apps.financial.services.report_service import ReportService

logger = logging.getLogger(__name__)


class ReportViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    ViewSet گزارش‌های مالی

    انواع گزارش:
    - daily, weekly, monthly, quarterly, yearly
    - custom range
    - خروجی JSON, CSV, Excel, PDF
    """
    queryset = FinancialReport.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, CanManageFinancial]

    def get_serializer_class(self):
        if self.action == 'generate':
            return ReportGenerateSerializer
        return ReportSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """تولید گزارش جدید"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            report = ReportService.generate_report(
                report_type=data['report_type'],
                from_date=data.get('from_date'),
                to_date=data.get('to_date'),
                format=data.get('format', 'json'),
                title=data.get('title', ''),
                filters={
                    'invoice_type': data.get('invoice_type'),
                    'status': data.get('status'),
                    'user_id': data.get('user_id'),
                    'payment_method': data.get('payment_method'),
                },
                generated_by=request.user,
            )

            logger.info(f"Report generated: {report.title}")

            return Response({
                'message': _('Report generated.'),
                'report': ReportSerializer(report, context={'request': request}).data,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """خلاصه گزارش امروز"""
        from django.utils import timezone

        today = timezone.now().date()
        summary = ReportService.get_daily_summary(today)

        return Response(summary)

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """خلاصه گزارش ماه جاری"""
        from django.utils import timezone

        today = timezone.now().date()
        summary = ReportService.get_monthly_summary(today.year, today.month)

        return Response(summary)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """دانلود فایل گزارش"""
        report = self.get_object()

        if report.report_file:
            return Response({
                'download_url': request.build_absolute_uri(report.report_file.url)
            })

        return Response({'error': _('No file available.')}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def quick_stats(self, request):
        """آمار سریع برای داشبورد"""
        from django.utils import timezone
        from django.db.models import Sum, Count
        from apps.financial.models import Invoice

        today = timezone.now().date()
        this_month = today.replace(day=1)

        invoices = Invoice.objects.all()

        stats = {
            'today': {
                'invoices': invoices.filter(created_at__date=today).count(),
                'amount': float(invoices.filter(created_at__date=today).aggregate(
                    Sum('total_amount'))['total_amount__sum'] or 0
                ),
                'paid': invoices.filter(paid_at__date=today).count(),
            },
            'this_month': {
                'invoices': invoices.filter(created_at__date__gte=this_month).count(),
                'amount': float(invoices.filter(created_at__date__gte=this_month).aggregate(
                    Sum('total_amount'))['total_amount__sum'] or 0
                ),
                'paid': float(invoices.filter(
                    status='paid', created_at__date__gte=this_month
                ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0),
            },
            'pending': {
                'count': invoices.filter(status__in=['pending', 'partially_paid']).count(),
                'amount': float(invoices.filter(
                    status__in=['pending', 'partially_paid']
                ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
            },
            'overdue': invoices.filter(
                status__in=['pending', 'partially_paid'],
                payment_due_date__lt=today
            ).count(),
        }

        return Response(stats)