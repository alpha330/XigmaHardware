from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.stock.models import ProductCategory
from apps.stock.enums import ProductCategoryType


class ProductCategorySerializer(serializers.ModelSerializer):
    """سریالایزر دسته‌بندی محصول"""
    category_type_display = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()
    full_path = serializers.CharField(read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'category_type', 'category_type_display',
            'condition', 'parent', 'children', 'ancestors', 'full_path',
            'description', 'icon', 'image',
            'level', 'sort_order', 'is_active', 'is_featured',
            'products_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'level', 'created_at', 'updated_at']

    def get_category_type_display(self, obj):
        return {
            'code': obj.category_type,
            'label': obj.get_category_type_display(),
        }

    def get_children(self, obj):
        """زیرمجموعه‌های مستقیم"""
        if obj.children.exists():
            return ProductCategorySerializer(
                obj.children.filter(is_active=True),
                many=True
            ).data
        return []

    def get_ancestors(self, obj):
        """مسیر از ریشه تا این دسته"""
        ancestors = obj.get_ancestors()
        return [{
            'id': str(a.id),
            'name': a.name,
            'slug': a.slug,
            'category_type': a.category_type,
        } for a in ancestors]

    def get_products_count(self, obj):
        """تعداد محصولات در این دسته و زیرمجموعه‌ها"""
        descendants = obj.get_descendants(include_self=True)
        from apps.stock.models import Product
        return Product.objects.filter(
            category__in=descendants,
            is_active=True
        ).count()


class ProductCategoryTreeSerializer(serializers.ModelSerializer):
    """سریالایزر درختی برای نمایش کامل"""
    children = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'category_type',
            'condition', 'children', 'level', 'is_active',
        ]

    def get_children(self, obj):
        if obj.children.filter(is_active=True).exists():
            return ProductCategoryTreeSerializer(
                obj.children.filter(is_active=True),
                many=True
            ).data
        return []


class ProductCategoryCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد دسته‌بندی"""

    class Meta:
        model = ProductCategory
        fields = [
            'name', 'category_type', 'condition',
            'parent', 'description', 'icon', 'image',
            'sort_order', 'is_active', 'is_featured',
        ]

    def validate(self, data):
        category_type = data.get('category_type')
        parent = data.get('parent')
        condition = data.get('condition')

        # سطح اول باید condition داشته باشه
        if not parent and category_type == 'condition' and not condition:
            raise serializers.ValidationError({
                'condition': _('Top-level condition category must specify condition.')
            })

        # parent باید از type قبلی باشه
        if parent:
            type_order = ['condition', 'usage', 'brand', 'type', 'series']
            if category_type not in type_order:
                raise serializers.ValidationError({
                    'category_type': _('Invalid category type.')
                })

            # parent باید یک سطح بالاتر باشه
            parent_idx = type_order.index(parent.category_type)
            current_idx = type_order.index(category_type)
            if current_idx != parent_idx + 1:
                raise serializers.ValidationError({
                    'parent': _('Parent category must be one level above.')
                })

        return data