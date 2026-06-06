import logging
import csv
import io
from datetime import date, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.financial.models import FinancialReport, Invoice, FinancialTransaction
from apps.financial.enums import ReportType, ReportFormat

logger = logging.getLogger(__name__)


class ReportService:
    """
    سرویس تولید گزارش‌های مالی

    انواع گزارش:
    - روزانه، هفتگی، ماهانه، فصلی، سالانه
    - بازه سفارشی
    - خروجی JSON, CSV, Excel
    """

    @classmethod
    def generate_report(cls, report_type, from_date=None, to_date=None,
                        format='json', title='', filters=None, generated_by=None):
        """
        تولید گزارش مالی

        Args:
            report_type: نوع گزارش
            from_date: از تاریخ
            to_date: تا تاریخ
            format: فرمت خروجی
            title: عنوان گزارش
            filters: فیلترهای اضافی
            generated_by: تولید کننده

        Returns:
            FinancialReport
        """
        # تنظیم تاریخ‌ها
        if not from_date:
            from_date = timezone.now().date()
        if not to_date:
            to_date = from_date

        if not title:
            title = cls._generate_title(report_type, from_date, to_date)

        # جمع‌آوری داده‌ها
        data = cls._collect_data(from_date, to_date, filters or {})

        # محاسبه خلاصه
        total_invoices = data.get('total_invoices', 0)
        total_amount = data.get('total_amount', 0)
        total_paid = data.get('total_paid', 0)
        total_discount = data.get('total_discount', 0)
        total_tax = data.get('total_tax', 0)

        # ایجاد گزارش
        report = FinancialReport.objects.create(
            title=title,
            report_type=report_type,
            format=format,
            from_date=from_date,
            to_date=to_date,
            generated_by=generated_by,
            parameters=filters or {},
            data=data,
            total_invoices=total_invoices,
            total_amount=total_amount,
            total_paid=total_paid,
            total_discount=total_discount,
            total_tax=total_tax,
        )

        # تولید فایل
        if format == 'csv':
            report.report_file = cls._generate_csv(data, title)
            report.save()

        logger.info(f"Report generated: {report.title}")

        return report

    @classmethod
    def get_daily_summary(cls, target_date=None):
        """
        خلاصه گزارش روزانه

        Args:
            target_date: تاریخ (پیش‌فرض امروز)

        Returns:
            dict
        """
        if not target_date:
            target_date = timezone.now().date()

        invoices = Invoice.objects.filter(created_at__date=target_date)
        transactions = FinancialTransaction.objects.filter(transaction_date__date=target_date)

        try:
            import jdatetime
            jalali_date = jdatetime.date.fromgregorian(date=target_date)
            date_display = jalali_date.strftime('%Y/%m/%d')
            weekday = jalali_date.strftime('%A')
        except ImportError:
            date_display = target_date.isoformat()
            weekday = target_date.strftime('%A')

        return {
            'date': target_date.isoformat(),
            'date_jalali': date_display,
            'weekday': weekday,
            'invoices': {
                'total': invoices.count(),
                'amount': float(invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                'paid': invoices.filter(status='paid').count(),
                'paid_amount': float(
                    invoices.filter(status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
                ),
                'pending': invoices.filter(status__in=['pending', 'partially_paid']).count(),
            },
            'transactions': {
                'total': transactions.count(),
                'amount': float(transactions.aggregate(Sum('amount'))['amount__sum'] or 0),
                'verified': transactions.filter(status='verified').count(),
                'pending': transactions.filter(status='pending').count(),
            },
        }

    @classmethod
    def get_monthly_summary(cls, year, month):
        """
        خلاصه گزارش ماهانه

        Args:
            year: سال
            month: ماه

        Returns:
            dict
        """
        from calendar import monthrange

        _, last_day = monthrange(year, month)
        from_date = date(year, month, 1)
        to_date = date(year, month, last_day)

        invoices = Invoice.objects.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
        transactions = FinancialTransaction.objects.filter(
            transaction_date__date__gte=from_date,
            transaction_date__date__lte=to_date
        )

        # گزارش روزانه در ماه
        daily_breakdown = []
        for day in range(1, last_day + 1):
            day_date = date(year, month, day)
            day_invoices = invoices.filter(created_at__date=day_date)
            day_transactions = transactions.filter(transaction_date__date=day_date)

            daily_breakdown.append({
                'day': day,
                'invoices': day_invoices.count(),
                'amount': float(day_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
                'transactions': day_transactions.count(),
            })

        try:
            import jdatetime
            jalali_date = jdatetime.date.fromgregorian(date=from_date)
            month_name = jalali_date.strftime('%B %Y')
        except ImportError:
            month_name = from_date.strftime('%B %Y')

        return {
            'year': year,
            'month': month,
            'month_name': month_name,
            'total_invoices': invoices.count(),
            'total_amount': float(invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
            'total_paid': float(
                invoices.filter(status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
            ),
            'total_transactions': transactions.count(),
            'daily_breakdown': daily_breakdown,
        }

    # ==================== Private Methods ====================

    @classmethod
    def _collect_data(cls, from_date, to_date, filters):
        """جمع‌آوری داده‌های گزارش"""
        invoices = Invoice.objects.filter(
            created_at__date__gte=from_date,
            created_at__date__lte=to_date
        )

        transactions = FinancialTransaction.objects.filter(
            transaction_date__date__gte=from_date,
            transaction_date__date__lte=to_date
        )

        # اعمال فیلترها
        if filters.get('invoice_type'):
            invoices = invoices.filter(invoice_type=filters['invoice_type'])

        if filters.get('status'):
            invoices = invoices.filter(status=filters['status'])

        if filters.get('user_id'):
            invoices = invoices.filter(user_id=filters['user_id'])
            transactions = transactions.filter(user_id=filters['user_id'])

        if filters.get('payment_method'):
            transactions = transactions.filter(payment_method=filters['payment_method'])

        # آمار فاکتورها
        invoice_stats = {
            'total_invoices': invoices.count(),
            'total_amount': float(invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0),
            'total_paid': float(invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0),
            'total_discount': float(invoices.aggregate(Sum('discount_amount'))['discount_amount__sum'] or 0),
            'total_tax': float(invoices.aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0),
            'by_type': {
                t: invoices.filter(invoice_type=t).count()
                for t in ['proforma', 'final', 'wallet_charge', 'refund']
            },
            'by_status': {
                s: invoices.filter(status=s).count()
                for s in ['draft', 'pending', 'paid', 'partially_paid', 'cancelled']
            },
        }

        # آمار تراکنش‌ها
        transaction_stats = {
            'total_transactions': transactions.count(),
            'total_amount': float(transactions.aggregate(Sum('amount'))['amount__sum'] or 0),
            'by_type': {
                t: transactions.filter(transaction_type=t).count()
                for t in ['payment', 'deposit', 'withdraw', 'refund', 'wallet_charge']
            },
            'by_status': {
                s: transactions.filter(status=s).count()
                for s in ['pending', 'verified', 'failed', 'refunded']
            },
        }

        return {
            'period': {
                'from': from_date.isoformat(),
                'to': to_date.isoformat(),
            },
            'invoices': invoice_stats,
            'transactions': transaction_stats,
        }

    @classmethod
    def _generate_title(cls, report_type, from_date, to_date):
        """تولید عنوان گزارش"""
        type_labels = {
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly',
            'quarterly': 'Quarterly',
            'yearly': 'Yearly',
            'custom': 'Custom',
        }

        try:
            import jdatetime
            from_jalali = jdatetime.date.fromgregorian(date=from_date)
            to_jalali = jdatetime.date.fromgregorian(date=to_date)
            date_range = f"{from_jalali.strftime('%Y/%m/%d')} - {to_jalali.strftime('%Y/%m/%d')}"
        except ImportError:
            date_range = f"{from_date} - {to_date}"

        return f"{type_labels.get(report_type, 'Report')}: {date_range}"

    @classmethod
    def _generate_csv(cls, data, title):
        """تولید فایل CSV"""
        from django.core.files.base import ContentFile

        output = io.StringIO()
        writer = csv.writer(output)

        # هدر
        writer.writerow([title])
        writer.writerow([])

        # اطلاعات دوره
        writer.writerow(['Period', data['period']['from'], 'to', data['period']['to']])
        writer.writerow([])

        # آمار فاکتورها
        writer.writerow(['INVOICES'])
        writer.writerow(['Total', data['invoices']['total_invoices']])
        writer.writerow(['Amount', data['invoices']['total_amount']])
        writer.writerow(['Paid', data['invoices']['total_paid']])
        writer.writerow(['Discount', data['invoices']['total_discount']])
        writer.writerow(['Tax', data['invoices']['total_tax']])
        writer.writerow([])

        # بر اساس نوع
        writer.writerow(['Type', 'Count'])
        for t, c in data['invoices']['by_type'].items():
            writer.writerow([t, c])
        writer.writerow([])

        # آمار تراکنش‌ها
        writer.writerow(['TRANSACTIONS'])
        writer.writerow(['Total', data['transactions']['total_transactions']])
        writer.writerow(['Amount', data['transactions']['total_amount']])

        content = output.getvalue()
        output.close()

        filename = f"report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return ContentFile(content.encode('utf-8'), name=filename)