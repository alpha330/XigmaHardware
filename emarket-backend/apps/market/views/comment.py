import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.market.models import ProductComment
from apps.market.serializers.comment import (
    CommentSerializer,
    CommentCreateSerializer,
    CommentListSerializer,
)
from apps.market.services.comment_service import CommentService

logger = logging.getLogger(__name__)


class CommentViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    ViewSet کامنت‌های محصولات

    Actions:
    - list: کامنت‌های یک محصول
    - create: نوشتن کامنت/پاسخ
    - update: ویرایش کامنت
    - destroy: حذف کامنت
    - replies: پاسخ‌های یک کامنت
    - pin: پین کردن (ادمین)
    """
    queryset = ProductComment.objects.filter(status='active')

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action == 'list':
            return CommentListSerializer
        return CommentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = ProductComment.objects.filter(status='active').select_related(
            'user'
        ).prefetch_related('replies')

        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id, parent__isnull=True)

        return queryset.order_by('-is_pinned', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """حذف نرم"""
        CommentService.delete_comment(instance)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """دریافت پاسخ‌های یک کامنت"""
        comment = self.get_object()
        replies = CommentService.get_replies(comment)

        serializer = CommentListSerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """پین/آزاد کردن کامنت (ادمین)"""
        if not request.user.is_superuser and request.user.role != 'super_admin':
            return Response({'error': _('Permission denied.')}, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        CommentService.toggle_pin(comment)

        return Response({
            'message': _('Comment pinned.' if comment.is_pinned else 'Comment unpinned.'),
            'is_pinned': comment.is_pinned,
        })

    @action(detail=True, methods=['post'])
    def hide(self, request, pk=None):
        """مخفی کردن کامنت (ادمین)"""
        if not request.user.is_superuser and request.user.role != 'super_admin':
            return Response({'error': _('Permission denied.')}, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        CommentService.hide_comment(comment)

        return Response({'message': _('Comment hidden.')})