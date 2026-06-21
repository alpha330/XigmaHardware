import logging
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status, generics, permissions, views,mixins
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from apps.accounts.serializers.auth import (
    EmailRegisterSerializer,
    MobileRegisterSerializer,
    LoginSerializer,
    OTPSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from apps.accounts.serializers.user import UserSerializer
from apps.accounts.services.auth_service import AuthService
from apps.accounts.tasks import send_verification_email, send_otp_sms

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailRegisterView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    generics.CreateAPIView
    ):
    """
    ثبت‌نام با ایمیل
    """
    serializer_class = EmailRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = AuthService.register_by_email(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
            )

            # ارسال ایمیل تایید
            send_verification_email.delay(str(user.id))

            # تولید توکن
            refresh = RefreshToken.for_user(user)

            # ثبت دستگاه
            AuthService.register_device(
                user=user,
                request=request
            )

            logger.info(f"New user registered with email: {user.email}")

            return Response({
                'message': _('Registration successful. Please verify your email.'),
                'user': UserSerializer(user, context={'request': request}).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Email registration failed: {str(e)}")
            return Response({
                'error': _('Registration failed. Please try again.')
            }, status=status.HTTP_400_BAD_REQUEST)


class MobileRegisterView(generics.CreateAPIView):
    """ثبت‌نام با موبایل"""
    serializer_class = MobileRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = AuthService.register_by_mobile(
                mobile=serializer.validated_data['mobile'],
                password=serializer.validated_data.get('password'),
            )

            refresh = RefreshToken.for_user(user)

            return Response({
                'message': _('Registration successful. OTP sent.'),
                'user': UserSerializer(user, context={'request': request}).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Mobile registration failed: {str(e)}")
            return Response({'error': str(e)}, status=400)


class LoginView(generics.GenericAPIView):
    """
    ورود کاربر با ایمیل/موبایل + رمز عبور، یا OTP
    اگر کاربر فقط موبایل را ارسال کند → OTP ارسال می‌شود.
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email    = serializer.validated_data.get('email')
        mobile   = serializer.validated_data.get('mobile')
        password = serializer.validated_data.get('password')
        otp_code = serializer.validated_data.get('otp_code')

        # شناسه اصلی برای کار با سرویس (ایمیل یا موبایل)
        identifier = email or mobile

        # -------------------------------
        # ۱) درخواست OTP (فقط شناسه، بدون رمز و OTP)
        # -------------------------------
        if identifier and not password and not otp_code:
            # ارسال identifier به جای mobile به سرویس
            otp_id = AuthService.send_login_otp(identifier)

            if otp_id:
                return Response({
                    'message': _('OTP sent to your email/mobile.'),
                    'otp_id': str(otp_id),
                    'expires_in': 120
                })
            else:
                return Response({
                    'error': _('Identifier not registered.')
                }, status=status.HTTP_404_NOT_FOUND)

        # -------------------------------
        # ۲) ورود با OTP
        # -------------------------------
        if identifier and otp_code:
            # سرویس باید متد authenticate_user را طوری داشته باشد که با identifier کار کند
            user = AuthService.authenticate_user(identifier=identifier, otp_code=otp_code)
            if not user:
                return Response({'error': _('Invalid or expired OTP.')}, status=status.HTTP_401_UNAUTHORIZED)

        # -------------------------------
        # ۳) ورود با رمز عبور
        # -------------------------------
        elif password and identifier:
            user = AuthService.authenticate_user(
                email=email,
                mobile=mobile,
                password=password
            )
            if not user:
                return Response({'error': _('Invalid credentials.')}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({'error': _('Provide password or OTP.')}, status=status.HTTP_400_BAD_REQUEST)

        # -------------------------------
        # ۴) بررسی وضعیت کاربر
        # -------------------------------
        if not user.is_active:
            return Response({
                'error': _('Your account is disabled.')
            }, status=status.HTTP_403_FORBIDDEN)

        if user.is_locked:
            return Response({
                'error': _('Account temporarily locked. Try again later.')
            }, status=status.HTTP_423_LOCKED)

        # -------------------------------
        # ۵) ورود موفق – به‌روزرسانی و تولید توکن
        # -------------------------------
        AuthService.update_login_info(user, request)
        AuthService.register_device(user, request)

        refresh = RefreshToken.for_user(user)

        logger.info(f"User logged in: {user.email or user.mobile}")

        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class LogoutView(views.APIView):
    """
    خروج کاربر و باطل کردن توکن
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # غیرفعال کردن دستگاه فعلی
            if hasattr(request, 'device'):
                request.device.is_active = False
                request.device.save()

            logger.info(f"User logged out: {request.user.email or request.user.mobile}")

            return Response({
                'message': _('Successfully logged out.')
            })

        except TokenError:
            return Response({
                'error': _('Invalid token.')
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response({
                'error': _('Logout failed.')
            }, status=status.HTTP_400_BAD_REQUEST)


class RequestOTPView(views.APIView):
    """درخواست کد OTP"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mobile = request.data.get('mobile')
        purpose = request.data.get('purpose', 'login')

        if not mobile:
            return Response({'error': _('Mobile number is required.')}, status=400)

        try:
            user = User.objects.get(mobile=mobile)

            # ارسال OTP
            success = AuthService.send_login_otp(mobile)

            return Response({
                'message': _('OTP sent successfully.'),
                'expires_in': 300,
            })

        except User.DoesNotExist:
            return Response({
                'message': _('If the mobile is registered, an OTP will be sent.'),
            })


class VerifyOTPView(views.APIView):
    """
    تایید کد OTP
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            from apps.accounts.models import OTPCode
            from django.db.models import Q

            otp_id = serializer.validated_data.get('otp_id')
            code = serializer.validated_data.get('code')
            # دریافت identifier (ایمیل یا موبایل) از سریالایزر
            mobile = serializer.validated_data.get('mobile')
            email = serializer.validated_data.get('email')
            identifier = mobile or email

            if not otp_id:
                return Response({'error': _('OTP ID is missing.')}, status=status.HTTP_400_BAD_REQUEST)

            # 🎯 اصلاح: فیلتر کردن کاربر بر اساس موبایل OR ایمیل
            otp = OTPCode.objects.get(
                id=otp_id,
                user__in=User.objects.filter(Q(mobile=identifier) | Q(email=identifier))
            )

            if otp.verify(code):
                user = otp.user
                # مشخص کردن اینکه کاربر موبایلی بوده یا ایمیلی برای متد verify
                if mobile:
                    user.verify_mobile()
                else:
                    user.verify_email() # اگر متد verify_email دارید

                refresh = RefreshToken.for_user(user)
                AuthService.update_login_info(user, request)

                if user.last_login is None:
                    AuthService.send_welcome_message(user)

                return Response({
                    'message': _('OTP verified successfully.'),
                    'user': UserSerializer(user, context={'request': request}).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
            else:
                return Response({'error': _('Invalid or expired OTP.')}, status=status.HTTP_400_BAD_REQUEST)

        except OTPCode.DoesNotExist:
            return Response({'error': _('Invalid OTP reference.')}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmailVerificationView(views.APIView):
    """
    تایید ایمیل کاربر
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        """
        تایید ایمیل با توکن
        """
        try:
            user = AuthService.verify_email_token(token)

            if user:
                user.verify_email()

                logger.info(f"Email verified for user: {user.email}")

                return Response({
                    'message': _('Email verified successfully.'),
                    'user': UserSerializer(user, context={'request': request}).data
                })
            else:
                return Response({
                    'error': _('Invalid or expired verification token.')
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}")
            return Response({
                'error': _('Verification failed.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        ارسال مجدد ایمیل تایید
        """
        if not request.user.is_authenticated:
            return Response({
                'error': _('Authentication required.')
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            if request.user.is_email_verified:
                return Response({
                    'message': _('Email is already verified.')
                })

            send_verification_email.delay(str(request.user.id))

            return Response({
                'message': _('Verification email sent.')
            })

        except Exception as e:
            logger.error(f"Resend verification email failed: {str(e)}")
            return Response({
                'error': _('Failed to send verification email.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MobileVerificationView(views.APIView):
    """تایید موبایل کاربر"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        action = request.data.get('action', 'verify')  # 'send' or 'verify'

        if action == 'send':
            # ارسال OTP جدید
            try:
                otp = AuthService.send_mobile_verification_otp(request.user)
                return Response({
                    'message': _('Verification OTP sent.'),
                    'expires_in': 300,
                })
            except ValueError as e:
                return Response({'error': str(e)}, status=400)

        elif action == 'verify':
            # تایید با OTP
            otp_id = request.data.get('otp_id')
            code = request.data.get('code')

            if not otp_id or not code:
                return Response({'error': _('OTP ID and code are required.')}, status=400)

            try:
                from apps.accounts.models import OTPCode
                otp = OTPCode.objects.get(
                    id=otp_id,
                    user=request.user,
                    purpose='verify_profile',
                    is_used=False,
                )

                if otp.verify(code):
                    request.user.verify_mobile()
                    return Response({'message': _('Mobile verified.')})
                else:
                    return Response({'error': _('Invalid or expired OTP.')}, status=400)

            except OTPCode.DoesNotExist:
                return Response({'error': _('Invalid OTP reference.')}, status=400)

        return Response({'error': _('Invalid action.')}, status=400)


class ChangePasswordView(views.APIView):
    """
    تغییر رمز عبور کاربر
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            # تغییر رمز عبور
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()

            # باطل کردن همه توکن‌های قبلی
            AuthService.revoke_all_tokens(request.user)

            # تولید توکن جدید
            refresh = RefreshToken.for_user(request.user)

            logger.info(f"Password changed for user: {request.user.email or request.user.mobile}")

            return Response({
                'message': _('Password changed successfully.'),
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })

        except Exception as e:
            logger.error(f"Password change failed: {str(e)}")
            return Response({
                'error': _('Failed to change password.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(views.APIView):
    """
    درخواست بازیابی رمز عبور
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            email_or_mobile = serializer.validated_data['email_or_mobile']

            # پیدا کردن کاربر با ایمیل یا موبایل
            user = AuthService.find_user_by_email_or_mobile(email_or_mobile)

            if user:
                # ارسال OTP یا ایمیل بازیابی
                if user.mobile:
                    from apps.accounts.models import OTPCode
                    otp = OTPCode.generate(
                        user=user,
                        purpose='reset_password',
                        sent_via='sms'
                    )
                    send_otp_sms.delay(user.mobile, otp.code)  # ✅ اصلاح شد

                    return Response({
                        'message': _('Password reset code sent to your mobile.'),
                        'otp_id': str(otp.id),
                        'reset_method': 'otp'
                    })

                elif user.email:
                    from apps.accounts.tasks import send_password_reset_email
                    send_password_reset_email.delay(str(user.id))

                    return Response({
                        'message': _('Password reset link sent to your email.'),
                        'reset_method': 'email'
                    })

            return Response({
                'message': _('If the account exists, a reset code/link will be sent.')
            })

        except Exception as e:
            logger.error(f"Password reset request failed: {str(e)}")
            return Response({
                'error': _('Failed to process reset request.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(views.APIView):
    """
    تایید و انجام بازیابی رمز عبور
    """
    permission_classes = [permissions.AllowAny]

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # پیدا کردن کاربر
            user = AuthService.find_user_by_email_or_mobile(
                serializer.validated_data['email_or_mobile']
            )

            if not user:
                return Response({
                    'error': _('Invalid request.')
                }, status=status.HTTP_400_BAD_REQUEST)

            # تایید OTP
            otp_id = serializer.validated_data.get('otp_id')
            code = serializer.validated_data.get('code')

            if otp_id and code:
                from apps.accounts.models import OTPCode
                try:
                    otp = OTPCode.objects.get(
                        id=otp_id,
                        user=user,
                        purpose='reset_password'
                    )
                except OTPCode.DoesNotExist:
                    return Response({
                        'error': _('Invalid OTP reference.')
                    }, status=status.HTTP_400_BAD_REQUEST)

                if not otp.verify(code):
                    return Response({
                        'error': _('Invalid or expired OTP.')
                    }, status=status.HTTP_400_BAD_REQUEST)

            # ✅ اول set_password بعد save
            user.set_password(serializer.validated_data['new_password'])
            user.reset_failed_login()
            user.save()  # ✅ ذخیره تغییرات

            # ✅ حالا توکن جدید بساز (با رمز جدید)
            AuthService.revoke_all_tokens(user)
            refresh = RefreshToken.for_user(user)

            logger.info(f"Password reset completed for user: {user.email or user.mobile}")

            return Response({
                'message': _('Password reset successful.'),
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })

        except Exception as e:
            logger.error(f"Password reset confirm failed: {str(e)}")
            return Response({
                'error': _('Failed to reset password.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestChangeOTPView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        new_value = request.data.get('value')  # موبایل یا ایمیل جدید
        contact_type = request.data.get('type') # 'mobile' یا 'email'

        if not new_value or contact_type not in ['mobile', 'email']:
            return Response({'error': _('Invalid data.')}, status=status.HTTP_400_BAD_REQUEST)
        from apps.accounts.models import OTPCode
        # تولید کد OTP با هدف CHANGE_CONTACT
        otp = OTPCode.generate(
            user=request.user,
            purpose='change_contact',
            sent_via=contact_type
        )

        # ارسال کد (استفاده از سرویس‌های موجود شما)
        if contact_type == 'mobile':
            AuthService.send_otp_sms(new_value, otp.code)
        else:
            AuthService.send_otp_email(new_value, otp.code)

        return Response({'otp_id': str(otp.id)})

class VerifyChangeOTPView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        otp_id = request.data.get('otp_id')
        code = request.data.get('code')
        new_value = request.data.get('value')
        contact_type = request.data.get('type')

        try:
            from apps.accounts.models import OTPCode
            # جستجوی کد مربوطه برای این کاربر با هدف تغییر اطلاعات
            otp = OTPCode.objects.get(id=otp_id, user=request.user, purpose='change_contact')

            # استفاده از متد verify موجود در مدل شما
            if otp.verify(code):
                # بروزرسانی دیتابیس کاربر
                if contact_type == 'mobile':
                    request.user.mobile = new_value
                else:
                    request.user.email = new_value
                request.user.save()

                return Response({'message': _('Contact info updated successfully.')})
            else:
                # ارور در صورت اشتباه بودن کد یا تمام شدن تلاش‌ها
                return Response({'error': _('Invalid or expired code.')}, status=status.HTTP_400_BAD_REQUEST)

        except OTPCode.DoesNotExist:
            return Response({'error': _('Invalid OTP reference.')}, status=status.HTTP_400_BAD_REQUEST)