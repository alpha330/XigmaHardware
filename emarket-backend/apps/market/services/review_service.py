import logging
from django.db import transaction as db_transaction
from django.utils.translation import gettext_lazy as _
from apps.market.models import ProductReview, ReviewLike
from apps.market.enums import ReviewStatus

logger = logging.getLogger(__name__)


class ReviewService:
    """
    سرویس مدیریت ریویوها

    عملیات:
    - ایجاد/ویرایش ریویو
    - لایک/دیسلایک
    - مدیریت وضعیت
    """

    @classmethod
    @db_transaction.atomic
    def create_review(cls, product, user, title, body, pros='', cons='', rating=None):
        """
        ایجاد ریویو جدید

        Args:
            product: محصول
            user: کاربر
            title: عنوان
            body: متن
            pros: نقاط قوت
            cons: نقاط ضعف
            rating: امتیاز (اختیاری)

        Returns:
            ProductReview
        """
        # چک تکراری
        if ProductReview.objects.filter(product=product, user=user).exists():
            raise ValueError(_('You have already reviewed this product.'))

        # چک خرید معتبر
        is_verified = cls._check_purchase(user, product)

        review = ProductReview.objects.create(
            product=product,
            user=user,
            title=title.strip(),
            body=body.strip(),
            pros=pros.strip(),
            cons=cons.strip(),
            rating=rating,
            is_verified_purchase=is_verified,
            status=ReviewStatus.PUBLISHED,
        )

        logger.info(f"Review created: {product.slug} by {user.email}")

        return review

    @classmethod
    @db_transaction.atomic
    def update_review(cls, review, data):
        """
        بروزرسانی ریویو

        Args:
            review: ریویو
            data: داده‌های جدید

        Returns:
            ProductReview
        """
        allowed = ['title', 'body', 'pros', 'cons']
        for field in allowed:
            if field in data:
                setattr(review, field, data[field])

        review.save()

        logger.info(f"Review updated: {review.id}")

        return review

    @classmethod
    @db_transaction.atomic
    def delete_review(cls, review):
        """حذف ریویو"""
        review.status = ReviewStatus.HIDDEN
        review.save()
        logger.info(f"Review hidden: {review.id}")

    @classmethod
    @db_transaction.atomic
    def like_review(cls, review, user, is_like=True):
        """
        لایک یا دیسلایک ریویو

        Args:
            review: ریویو
            user: کاربر
            is_like: True=Like, False=Dislike

        Returns:
            dict: وضعیت جدید
        """
        existing = ReviewLike.objects.filter(review=review, user=user).first()

        if existing:
            if existing.is_like == is_like:
                # حذف لایک قبلی
                existing.delete()
                action = 'removed'
            else:
                # تغییر لایک به دیسلایک یا برعکس
                existing.is_like = is_like
                existing.save()
                action = 'changed'
        else:
            # لایک جدید
            ReviewLike.objects.create(review=review, user=user, is_like=is_like)
            action = 'added'

        # بروزرسانی شمارنده‌ها
        review.likes_count = review.likes.filter(is_like=True).count()
        review.dislikes_count = review.likes.filter(is_like=False).count()
        review.save(update_fields=['likes_count', 'dislikes_count'])

        logger.info(f"Review {review.id} {action} {'like' if is_like else 'dislike'} by {user.email}")

        return {
            'action': action,
            'likes_count': review.likes_count,
            'dislikes_count': review.dislikes_count,
            'user_has_liked': is_like if action != 'removed' else None,
        }

    @classmethod
    def get_reviews_for_product(cls, product, status='published', sort_by='-created_at'):
        """
        دریافت ریویوهای یک محصول

        Args:
            product: محصول
            status: وضعیت
            sort_by: مرتب‌سازی

        Returns:
            QuerySet
        """
        queryset = product.reviews.filter(status=status).select_related(
            'user', 'rating'
        ).prefetch_related('likes')

        # مرتب‌سازی
        sort_options = {
            '-created_at': '-created_at',
            'created_at': 'created_at',
            '-likes': '-likes_count',
            'verified': '-is_verified_purchase',
        }

        return queryset.order_by(sort_options.get(sort_by, '-created_at'))

    @classmethod
    def get_user_review_for_product(cls, product, user):
        """
        دریافت ریویو کاربر برای محصول

        Args:
            product: محصول
            user: کاربر

        Returns:
            ProductReview or None
        """
        return ProductReview.objects.filter(
            product=product, user=user
        ).exclude(status=ReviewStatus.HIDDEN).first()

    @classmethod
    def _check_purchase(cls, user, product):
        """چک خرید معتبر"""
        from apps.financial.models import InvoiceItem

        return InvoiceItem.objects.filter(
            invoice__user=user,
            invoice__status='paid',
            product=product.stock_product,
        ).exists()