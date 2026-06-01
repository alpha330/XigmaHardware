"""
Factory Boy Factories for Test Data
نصب: pip install factory-boy
"""

import factory
import factory.fuzzy
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile, Wallet, UserDevice, OTPCode
from apps.accounts.enums import UserRole, ProfileType

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory برای ساخت کاربر تست
    """
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    mobile = factory.Sequence(lambda n: f'09{n:09d}'[:11])
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'TestPass123!')
    is_active = True
    is_email_verified = True
    is_mobile_verified = True
    role = UserRole.CLIENT
    registration_method = 'email'
    
    @factory.lazy_attribute
    def email(self):
        """ایمیل یکتا"""
        return f'user{User.objects.count() + 1}@example.com'
    
    class Params:
        # کاربر با ایمیل
        with_email = factory.Trait(
            registration_method='email',
            mobile=None
        )
        # کاربر با موبایل
        with_mobile = factory.Trait(
            registration_method='mobile',
            email=None
        )
        # کاربر سوپر ادمین
        super_admin = factory.Trait(
            role=UserRole.SUPER_ADMIN,
            is_staff=True,
            is_superuser=True
        )
        # کاربر حسابدار
        accountant = factory.Trait(
            role=UserRole.ACCOUNTANT
        )
        # کاربر تایید نشده
        unverified = factory.Trait(
            is_email_verified=False,
            is_mobile_verified=False
        )
        # کاربر غیرفعال
        inactive = factory.Trait(
            is_active=False
        )


class ProfileFactory(factory.django.DjangoModelFactory):
    """
    Factory برای ساخت پروفایل
    """
    class Meta:
        model = Profile
    
    user = factory.SubFactory(UserFactory)
    profile_type = ProfileType.INDIVIDUAL
    national_code = factory.Sequence(lambda n: f'{n:010d}'[:10])
    address = factory.Faker('address')
    postal_code = factory.Sequence(lambda n: f'{n:010d}'[:10])
    tel = factory.Sequence(lambda n: f'021{n:08d}'[:11])
    
    class Params:
        # پروفایل حقوقی
        legal = factory.Trait(
            profile_type=ProfileType.LEGAL,
            company_name=factory.Faker('company'),
            national_id=factory.Sequence(lambda n: f'{n:011d}'[:11]),
            economic_code=factory.Sequence(lambda n: f'{n:012d}'[:12]),
            national_code=None
        )
        # پروفایل ناقص
        incomplete = factory.Trait(
            national_code=None,
            address='',
            postal_code='',
            is_completed=False
        )


class WalletFactory(factory.django.DjangoModelFactory):
    """
    Factory برای ساخت کیف پول
    """
    class Meta:
        model = Wallet
    
    user = factory.SubFactory(UserFactory)
    balance = factory.fuzzy.FuzzyDecimal(0, 10000000, 2)
    is_active = True


class UserDeviceFactory(factory.django.DjangoModelFactory):
    """
    Factory برای ساخت دستگاه
    """
    class Meta:
        model = UserDevice
    
    user = factory.SubFactory(UserFactory)
    device_name = factory.Faker('user_agent')
    device_type = 'Desktop'
    operating_system = 'Windows'
    browser = 'Chrome'
    ip_address = factory.Faker('ipv4')
    is_active = True
    is_trusted = False


class OTPCodeFactory(factory.django.DjangoModelFactory):
    """
    Factory برای ساخت کد OTP
    """
    class Meta:
        model = OTPCode
    
    user = factory.SubFactory(UserFactory)
    code = factory.fuzzy.FuzzyText(length=6, chars='0123456789')
    purpose = 'login'
    sent_via = 'sms'
    is_used = False
    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timezone.timedelta(minutes=5)
    )