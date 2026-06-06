import logging
from django.db import transaction as db_transaction
from django.utils.translation import gettext_lazy as _
from apps.market.models import ProductComment
from apps.market.enums import CommentStatus

logger = logging.getLogger(__name__)


class CommentService:
    """
    سرویس مدیریت کامنت‌ها

    عملیات:
    - ایجاد کامنت/پاسخ
    - ویرایش
    - حذف نرم
    - پین کردن
    """

    @classmethod
    @db_transaction.atomic
    def create_comment(cls, product, user, body, parent=None):
        """
        ایجاد کامنت یا پاسخ

        Args:
            product: محصول
            user: کاربر
            body: متن
            parent: کامنت والد (برای پاسخ)

        Returns:
            ProductComment
        """
        if parent:
            # پاسخ به کامنت
            if parent.product != product:
                raise ValueError(_('Parent comment must belong to same product.'))

            if parent.parent is not None:
                raise ValueError(_('Cannot reply to a reply. Reply to main comment.'))

            if parent.status != CommentStatus.ACTIVE:
                raise ValueError(_('Cannot reply to deleted comment.'))

        comment = ProductComment.objects.create(
            product=product,
            user=user,
            body=body.strip(),
            parent=parent,
            status=CommentStatus.ACTIVE,
        )

        logger.info(
            f"Comment {'reply' if parent else ''} created: "
            f"{product.slug} by {user.email}"
        )

        return comment

    @classmethod
    @db_transaction.atomic
    def update_comment(cls, comment, body):
        """
        ویرایش کامنت

        Args:
            comment: کامنت
            body: متن جدید

        Returns:
            ProductComment
        """
        comment.body = body.strip()
        comment.is_edited = True
        comment.save()

        logger.info(f"Comment updated: {comment.id}")

        return comment

    @classmethod
    @db_transaction.atomic
    def delete_comment(cls, comment):
        """
        حذف نرم کامنت

        Args:
            comment: کامنت
        """
        comment.soft_delete()
        logger.info(f"Comment deleted: {comment.id}")

    @classmethod
    @db_transaction.atomic
    def toggle_pin(cls, comment):
        """
        پین/آزاد کردن کامنت

        Args:
            comment: کامنت

        Returns:
            ProductComment
        """
        comment.is_pinned = not comment.is_pinned
        comment.save(update_fields=['is_pinned'])

        logger.info(f"Comment {'pinned' if comment.is_pinned else 'unpinned'}: {comment.id}")

        return comment

    @classmethod
    @db_transaction.atomic
    def hide_comment(cls, comment):
        """مخفی کردن کامنت"""
        comment.status = CommentStatus.HIDDEN
        comment.save()
        logger.info(f"Comment hidden: {comment.id}")

    @classmethod
    def get_comments_for_product(cls, product, parent_only=True):
        """
        دریافت کامنت‌های یک محصول

        Args:
            product: محصول
            parent_only: فقط کامنت‌های اصلی

        Returns:
            QuerySet
        """
        queryset = product.comments.filter(status=CommentStatus.ACTIVE).select_related(
            'user'
        ).prefetch_related('replies')

        if parent_only:
            queryset = queryset.filter(parent__isnull=True)

        return queryset.order_by('-is_pinned', '-created_at')

    @classmethod
    def get_replies(cls, comment):
        """
        دریافت پاسخ‌های یک کامنت

        Args:
            comment: کامنت اصلی

        Returns:
            QuerySet
        """
        return comment.replies.filter(status=CommentStatus.ACTIVE).order_by('created_at')