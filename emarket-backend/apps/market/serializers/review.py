from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.market.models import ProductReview, ReviewLike


class ReviewLikeSerializer(serializers.ModelSerializer):
    """سریالایزر لایک/دیسلایک"""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = ReviewLike
        fields = ['id', 'review', 'user', 'user_name', 'is_like', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def get_user_name(self, obj):
        return obj.user.get_display_name()


class ReviewListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست ریویوها (خلاصه)"""
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    pros_list = serializers.SerializerMethodField()
    cons_list = serializers.SerializerMethodField()
    rating_overall = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = [
            'id', 'user', 'user_name', 'user_avatar',
            'title', 'body_short',
            'pros_list', 'cons_list',
            'rating_overall',
            'is_verified_purchase',
            'likes_count', 'dislikes_count',
            'status', 'created_at',
        ]

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def get_user_avatar(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None

    def get_pros_list(self, obj):
        return obj.get_pros_list()[:3]

    def get_cons_list(self, obj):
        return obj.get_cons_list()[:3]

    def get_rating_overall(self, obj):
        if obj.rating:
            return obj.rating.overall
        return None

    @property
    def body_short(self):
        return self.body[:200] + '...' if len(self.body) > 200 else self.body


class ReviewSerializer(serializers.ModelSerializer):
    """سریالایزر کامل ریویو"""
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    pros_list = serializers.SerializerMethodField()
    cons_list = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'user', 'user_name', 'user_avatar',
            'title', 'body', 'pros', 'cons',
            'pros_list', 'cons_list',
            'rating',
            'is_verified_purchase',
            'likes_count', 'dislikes_count', 'likes',
            'status', 'status_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'likes_count', 'dislikes_count', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def get_user_avatar(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None

    def get_pros_list(self, obj):
        return obj.get_pros_list()

    def get_cons_list(self, obj):
        return obj.get_cons_list()

    def get_rating(self, obj):
        if obj.rating:
            from .rating import RatingSerializer
            return RatingSerializer(obj.rating, context=self.context).data
        return None

    def get_likes(self, obj):
        """نمایش وضعیت لایک کاربر جاری"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_like = obj.likes.filter(user=request.user).first()
            if user_like:
                return {
                    'user_has_liked': user_like.is_like,
                    'user_has_disliked': not user_like.is_like,
                }
        return {'user_has_liked': False, 'user_has_disliked': False}

    def get_status_display(self, obj):
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
        }


class ReviewCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد ریویو"""

    class Meta:
        model = ProductReview
        fields = [
            'product', 'title', 'body',
            'pros', 'cons',
        ]

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(_('Title must be at least 5 characters.'))
        return value.strip()

    def validate_body(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError(_('Review must be at least 20 characters.'))
        return value.strip()

    def validate(self, data):
        user = self.context['request'].user
        product = data.get('product')

        # چک نکنه قبلاً ریویو داده
        if ProductReview.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                _('You have already reviewed this product.')
            )

        return data