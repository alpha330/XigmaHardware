from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User, Profile, Wallet


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    ایجاد خودکار پروفایل هنگام ساخت کاربر
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    ایجاد خودکار کیف پول هنگام ساخت کاربر
    """
    if created:
        Wallet.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    ذخیره پروفایل همراه با کاربر
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()