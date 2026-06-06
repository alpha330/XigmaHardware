from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.market.models import ProductMedia


class ProductMediaSerializer(serializers.ModelSerializer):
    """سریالایزر مدیا محصول"""
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    media_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ProductMedia
        fields = [
            'id', 'product', 'media_type', 'media_type_display',
            'image', 'image_url', 'video_url',
            'video_thumbnail', 'thumbnail_url',
            'title', 'alt_text',
            'sort_order', 'is_main',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_thumbnail_url(self, obj):
        if obj.video_thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_thumbnail.url)
            return obj.video_thumbnail.url
        return None

    def get_media_type_display(self, obj):
        return {
            'code': obj.media_type,
            'label': obj.get_media_type_display(),
            'icon': {
                'image': '🖼️',
                'video': '🎬',
                'gallery': '📸',
            }.get(obj.media_type, '📁')
        }


class ProductMediaCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد/آپلود مدیا"""

    class Meta:
        model = ProductMedia
        fields = [
            'product', 'media_type', 'image', 'video_url',
            'video_thumbnail', 'title', 'alt_text',
            'sort_order', 'is_main',
        ]

    def validate(self, data):
        media_type = data.get('media_type')

        if media_type in ['image', 'gallery'] and not data.get('image'):
            raise serializers.ValidationError({
                'image': _('Image is required for image/gallery type.')
            })

        if media_type == 'video' and not data.get('video_url'):
            raise serializers.ValidationError({
                'video_url': _('Video URL is required for video type.')
            })

        # اگر is_main هست، بقیه رو false کن
        if data.get('is_main'):
            product = data.get('product')
            if product:
                ProductMedia.objects.filter(product=product).update(is_main=False)

        return data

    def validate_image(self, value):
        if value:
            # محدودیت حجم (10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError(_('Image size must be less than 10MB.'))

            # محدودیت فرمت
            allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    _('Image must be JPEG, PNG, WebP, or GIF format.')
                )
        return value