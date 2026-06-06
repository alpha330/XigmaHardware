import logging
from django.db import transaction as db_transaction
from django.utils.translation import gettext_lazy as _
from apps.market.models import ProductRating

logger = logging.getLogger(__name__)


class RatingService:
    """
    سرویس مدیریت امتیازدهی

    عملیات:
    - ثبت/بروزرسانی امتیاز
    - محاسبه میانگین
    - بررسی خرید معتبر
    """

    @classmethod
    @db_transaction.atomic
    def rate_product(cls, product, user, value_for_money, quality, performance, overall):
        """
        ثبت یا بروزرسانی امتیاز

        Args:
            product: محصول مارکت
            user: کاربر
            value_for_money: ارزش خرید (۱-۵)
            quality: کیفیت (۱-۵)
            performance: کارایی (۱-۵)
            overall: امتیاز کلی (۱-۵)

        Returns:
            tuple: (ProductRating, created)
        """
        # اعتبارسنجی
        for val in [value_for_money, quality, performance, overall]:
            if not 1 <= val <= 5:
                raise ValueError(_('Rating must be between 1 and 5.'))

        # چک کن آیا کاربر این محصول رو خریده
        is_verified = cls._check_verified_purchase(user, product)

        # ایجاد یا بروزرسانی
        rating, created = ProductRating.objects.update_or_create(
            product=product,
            user=user,
            defaults={
                'value_for_money': value_for_money,
                'quality': quality,
                'performance': performance,
                'overall': overall,
                'is_verified_purchase': is_verified,
                'is_active': True,
            }
        )

        # بروزرسانی کش محصول
        product.update_ratings_cache()

        action = 'created' if created else 'updated'
        logger.info(
            f"Rating {action}: {product.slug} by {user.email} - Overall: {overall}/5"
        )

        return rating, created

    @classmethod
    @db_transaction.atomic
    def delete_rating(cls, product, user):
        """
        حذف امتیاز (soft delete)

        Args:
            product: محصول
            user: کاربر
        """
        try:
            rating = ProductRating.objects.get(product=product, user=user, is_active=True)
            rating.is_active = False
            rating.save()

            # بروزرسانی کش
            product.update_ratings_cache()

            logger.info(f"Rating deleted: {product.slug} by {user.email}")
            return True
        except ProductRating.DoesNotExist:
            return False

    @classmethod
    def get_user_rating(cls, product, user):
        """
        دریافت امتیاز کاربر برای یک محصول

        Args:
            product: محصول
            user: کاربر

        Returns:
            ProductRating or None
        """
        return ProductRating.objects.filter(
            product=product, user=user, is_active=True
        ).first()

    @classmethod
    def get_rating_summary(cls, product):
        """
        خلاصه امتیازات یک محصول

        Args:
            product: محصول

        Returns:
            dict
        """
        from django.db.models import Count

        ratings = product.ratings.filter(is_active=True)
        count = ratings.count()

        if count == 0:
            return {
                'count': 0,
                'overall_avg': 0,
                'value_for_money_avg': 0,
                'quality_avg': 0,
                'performance_avg': 0,
                'distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            }

        # توزیع امتیازات
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        stats = ratings.values('overall').annotate(count=Count('overall'))
        for stat in stats:
            distribution[stat['overall']] = stat['count']

        return {
            'count': count,
            'overall_avg': float(product.avg_rating),
            'value_for_money_avg': float(product.avg_value_for_money),
            'quality_avg': float(product.avg_quality),
            'performance_avg': float(product.avg_performance),
            'distribution': distribution,
            'verified_count': ratings.filter(is_verified_purchase=True).count(),
        }

    @classmethod
    def _check_verified_purchase(cls, user, product):
        """
        بررسی اینکه کاربر این محصول رو خریده یا نه

        Args:
            user: کاربر
            product: محصول

        Returns:
            bool
        """
        # چک توی invoice items
        from apps.financial.models import InvoiceItem

        bought = InvoiceItem.objects.filter(
            invoice__user=user,
            invoice__status='paid',
            product=product.stock_product,
        ).exists()

        return bought