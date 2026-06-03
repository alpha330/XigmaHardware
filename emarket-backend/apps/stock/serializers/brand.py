from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.stock.models import Brand, BrandSeries


class BrandSeriesSerializer(serializers.ModelSerializer):
    """سریالایزر سری برند"""
    full_name = serializers.CharField(read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = BrandSeries
        fields = [
            'id', 'brand', 'name', 'slug', 'full_name',
            'year_released', 'generation', 'category',
            'description', 'is_active',
            'products_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


class BrandSerializer(serializers.ModelSerializer):
    """سریالایزر برند"""
    series = serializers.SerializerMethodField()
    products_count = serializers.IntegerField(read_only=True)
    active_products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'persian_name', 'slug',
            'logo', 'website', 'country',
            'description', 'warranty_info',
            'is_active', 'is_partner', 'popularity_score',
            'series', 'products_count', 'active_products_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'popularity_score', 'created_at', 'updated_at']

    def get_series(self, obj):
        """سری‌های فعال"""
        series = obj.series.filter(is_active=True)[:20]
        return BrandSeriesSerializer(series, many=True).data


class BrandCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد برند"""

    class Meta:
        model = Brand
        fields = [
            'name', 'persian_name', 'logo', 'website', 'country',
            'description', 'warranty_info', 'is_active', 'is_partner',
        ]

    def validate_name(self, value):
        if Brand.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(_('This brand already exists.'))
        return value


class BrandSeriesCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد سری برند"""

    class Meta:
        model = BrandSeries
        fields = [
            'brand', 'name', 'year_released', 'generation',
            'category', 'description', 'is_active',
        ]

    def validate(self, data):
        brand = data.get('brand')
        name = data.get('name')

        if BrandSeries.objects.filter(brand=brand, name__iexact=name).exists():
            raise serializers.ValidationError({
                'name': _('This series already exists for this brand.')
            })

        return data