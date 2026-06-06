from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.financial.models import FinancialReport
from apps.financial.enums import ReportType, ReportFormat


class ReportSerializer(serializers.ModelSerializer):
    """سریالایزر گزارش"""
    generated_by_name = serializers.SerializerMethodField()
    report_type_display = serializers.SerializerMethodField()
    date_range_display = serializers.SerializerMethodField()
    created_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = FinancialReport
        fields = [
            'id', 'title', 'report_type', 'report_type_display',
            'format', 'from_date', 'to_date', 'date_range_display',
            'generated_by', 'generated_by_name',
            'parameters', 'data',
            'total_invoices', 'total_amount', 'total_paid',
            'total_discount', 'total_tax',
            'report_file', 'notes',
            'created_at', 'created_at_jalali',
        ]
        read_only_fields = [
            'id', 'generated_by', 'data', 'report_file',
            'total_invoices', 'total_amount', 'total_paid',
            'total_discount', 'total_tax', 'created_at',
        ]

    def get_generated_by_name(self, obj):
        return obj.generated_by.get_display_name() if obj.generated_by else 'N/A'

    def get_report_type_display(self, obj):
        return {
            'code': obj.report_type,
            'label': obj.get_report_type_display(),
            'icon': {
                'daily': '📅',
                'weekly': '📊',
                'monthly': '📈',
                'quarterly': '📉',
                'yearly': '🗓️',
                'custom': '🔍',
            }.get(obj.report_type, '📊')
        }

    def get_date_range_display(self, obj):
        try:
            import jdatetime
            from_date = jdatetime.date.fromgregorian(date=obj.from_date)
            to_date = jdatetime.date.fromgregorian(date=obj.to_date)
            return f"{from_date.strftime('%Y/%m/%d')} - {to_date.strftime('%Y/%m/%d')}"
        except ImportError:
            return f"{obj.from_date} - {obj.to_date}"

    def get_created_at_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        except ImportError:
            return None


class ReportGenerateSerializer(serializers.Serializer):
    """سریالایزر تولید گزارش"""
    report_type = serializers.ChoiceField(choices=ReportType.choices, default='daily')
    format = serializers.ChoiceField(choices=ReportFormat.choices, default='json')
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    title = serializers.CharField(required=False, allow_blank=True, max_length=200)

    # فیلترهای اضافی
    invoice_type = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.UUIDField(required=False)
    payment_method = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        report_type = data.get('report_type')
        from_date = data.get('from_date')
        to_date = data.get('to_date')

        today = timezone.now().date()

        # تنظیم بازه زمانی بر اساس نوع گزارش
        if report_type == 'daily':
            if not from_date:
                data['from_date'] = today
            data['to_date'] = data['from_date']

        elif report_type == 'weekly':
            if not from_date:
                # از شنبه تا امروز
                days_since_saturday = (today.weekday() + 2) % 7
                data['from_date'] = today - timezone.timedelta(days=days_since_saturday)
            data['to_date'] = data['from_date'] + timezone.timedelta(days=6)

        elif report_type == 'monthly':
            if not from_date:
                data['from_date'] = today.replace(day=1)
            # آخرین روز ماه
            next_month = data['from_date'].replace(day=28) + timezone.timedelta(days=4)
            data['to_date'] = next_month - timezone.timedelta(days=next_month.day)

        elif report_type == 'quarterly':
            if not from_date:
                current_quarter = (today.month - 1) // 3
                data['from_date'] = today.replace(month=current_quarter * 3 + 1, day=1)
            # آخرین روز فصل
            month = ((data['from_date'].month - 1) // 3 + 1) * 3
            next_month = data['from_date'].replace(month=month, day=28) + timezone.timedelta(days=4)
            data['to_date'] = next_month - timezone.timedelta(days=next_month.day)

        elif report_type == 'yearly':
            if not from_date:
                data['from_date'] = today.replace(month=1, day=1)
            data['to_date'] = today.replace(month=12, day=31)

        else:  # custom
            if not from_date or not to_date:
                raise serializers.ValidationError(
                    _('From date and to date are required for custom reports.')
                )

        if data['from_date'] > data['to_date']:
            raise serializers.ValidationError(
                _('From date cannot be after to date.')
            )

        return data


class DailyReportSerializer(serializers.Serializer):
    """سریالایزر گزارش روزانه"""
    date = serializers.DateField()
    date_jalali = serializers.SerializerMethodField()
    total_invoices = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=15, decimal_places=2)
    invoices_by_type = serializers.DictField()
    transactions_count = serializers.IntegerField()

    def get_date_jalali(self, obj):
        try:
            import jdatetime
            return jdatetime.date.fromgregorian(date=obj['date']).strftime('%Y/%m/%d')
        except ImportError:
            return str(obj['date'])


class MonthlyReportSerializer(serializers.Serializer):
    """سریالایزر گزارش ماهانه"""
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    month_name = serializers.SerializerMethodField()
    total_invoices = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=15, decimal_places=2)
    daily_breakdown = serializers.ListField()

    def get_month_name(self, obj):
        import jdatetime
        return jdatetime.date(obj['year'], obj['month'], 1).strftime('%B %Y')