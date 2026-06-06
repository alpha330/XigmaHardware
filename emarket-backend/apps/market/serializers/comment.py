from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from apps.market.models import ProductComment


class CommentListSerializer(serializers.ModelSerializer):
    """سریالایزر لیست کامنت‌ها"""
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(read_only=True)
    is_reply = serializers.BooleanField(read_only=True)
    status_display = serializers.SerializerMethodField()
    created_at_display = serializers.SerializerMethodField()
    body_short = serializers.SerializerMethodField()

    class Meta:
        model = ProductComment
        fields = [
            'id', 'product', 'user', 'user_name', 'user_avatar',
            'parent', 'is_reply', 'body_short',
            'replies_count',
            'is_pinned', 'is_edited',
            'status', 'status_display',
            'created_at', 'created_at_display',
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

    def get_status_display(self, obj):
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
        }

    def get_created_at_display(self, obj):
        """نمایش نسبی زمان"""
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 30:
            return f'{diff.days // 30} months ago'
        elif diff.days > 0:
            return f'{diff.days} days ago'
        elif diff.seconds > 3600:
            return f'{diff.seconds // 3600} hours ago'
        elif diff.seconds > 60:
            return f'{diff.seconds // 60} minutes ago'
        return 'Just now'

    @property
    def body_short(self):
        if hasattr(self, 'body') and self.body:
            return self.body[:100] + '...' if len(self.body) > 100 else self.body
        return ''


class CommentSerializer(serializers.ModelSerializer):
    """سریالایزر کامل کامنت (با replies)"""
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(read_only=True)
    status_display = serializers.SerializerMethodField()
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = ProductComment
        fields = [
            'id', 'product', 'user', 'user_name', 'user_avatar',
            'parent', 'body',
            'replies', 'replies_count',
            'is_pinned', 'is_edited',
            'status', 'status_display',
            'created_at', 'created_at_display', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'is_edited', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.get_display_name()

    def get_user_avatar(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile.avatar.url)
            return obj.user.profile.avatar.url
        return None

    def get_replies(self, obj):
        """دریافت پاسخ‌ها (فقط سطح اول)"""
        replies = obj.replies.filter(status='active')[:5]
        return CommentListSerializer(replies, many=True, context=self.context).data

    def get_status_display(self, obj):
        return {
            'code': obj.status,
            'label': obj.get_status_display(),
        }

    def get_created_at_display(self, obj):
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 365:
            return f'{diff.days // 365} years ago'
        elif diff.days > 30:
            return f'{diff.days // 30} months ago'
        elif diff.days > 0:
            return f'{diff.days} days ago'
        elif diff.seconds > 3600:
            return f'{diff.seconds // 3600} hours ago'
        elif diff.seconds > 60:
            return f'{diff.seconds // 60} minutes ago'
        return 'Just now'


class CommentCreateSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد کامنت"""

    class Meta:
        model = ProductComment
        fields = ['product', 'parent', 'body']

    def validate_body(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(_('Comment must be at least 2 characters.'))
        if len(value) > 2000:
            raise serializers.ValidationError(_('Comment must be less than 2000 characters.'))
        return value.strip()

    def validate_parent(self, value):
        """اعتبارسنجی parent"""
        if value:
            # parent باید کامنت اصلی باشه (نه reply)
            if value.parent is not None:
                raise serializers.ValidationError(
                    _('Cannot reply to a reply. Reply to the main comment.')
                )
            # parent باید فعال باشه
            if value.status != 'active':
                raise serializers.ValidationError(
                    _('Cannot reply to a deleted/hidden comment.')
                )
        return value