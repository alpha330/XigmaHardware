import logging
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import status, generics, permissions, views
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


class EmailRegisterView(generics.CreateAPIView):
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
    """
    ثبت‌نام با موبایل
    """
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
            
            # ارسال OTP
            from apps.accounts.models import OTPCode
            otp = OTPCode.generate(
                user=user,
                purpose='register',
                sent_via='sms'
            )
            
            # ارسال SMS (در محیط واقعی)
            send_otp_sms.delay(str(user.id), otp.code)
            
            # تولید توکن
            refresh = RefreshToken.for_user(user)
            
            # ثبت دستگاه
            AuthService.register_device(
                user=user,
                request=request
            )
            
            logger.info(f"New user registered with mobile: {user.mobile}")
            
            return Response({
                'message': _('Registration successful. Please verify your mobile.'),
                'user': UserSerializer(user, context={'request': request}).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'otp_id': str(otp.id)  # فقط در محیط توسعه
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Mobile registration failed: {str(e)}")
            return Response({
                'error': _('Registration failed. Please try again.')
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """
    ورود کاربر با ایمیل یا موبایل
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = AuthService.authenticate_user(
                email=serializer.validated_data.get('email'),
                mobile=serializer.validated_data.get('mobile'),
                password=serializer.validated_data.get('password'),
            )
            
            if not user:
                return Response({
                    'error': _('Invalid credentials.')
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({
                    'error': _('Your account is disabled.')
                }, status=status.HTTP_403_FORBIDDEN)
            
            if user.is_locked:
                return Response({
                    'error': _('Your account is temporarily locked. Try again later.')
                }, status=status.HTTP_423_LOCKED)
            
            # به‌روزرسانی اطلاعات ورود
            AuthService.update_login_info(user, request)
            
            # تولید توکن
            refresh = RefreshToken.for_user(user)
            
            # ثبت دستگاه
            AuthService.register_device(user, request)
            
            logger.info(f"User logged in: {user.email or user.mobile}")
            
            return Response({
                'user': UserSerializer(user, context={'request': request}).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response({
                'error': _('Login failed. Please try again.')
            }, status=status.HTTP_400_BAD_REQUEST)


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
    """
    درخواست کد OTP
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        mobile = request.data.get('mobile')
        purpose = request.data.get('purpose', 'login')
        
        if not mobile:
            return Response({
                'error': _('Mobile number is required.')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(mobile=mobile)
            
            # تولید OTP
            from apps.accounts.models import OTPCode
            otp = OTPCode.generate(
                user=user,
                purpose=purpose,
                sent_via='sms'
            )
            
            # ارسال SMS
            send_otp_sms.delay(str(user.id), otp.code)
            
            logger.info(f"OTP requested for {mobile}, purpose: {purpose}")
            
            return Response({
                'message': _('OTP sent successfully.'),
                'otp_id': str(otp.id),  # فقط در محیط توسعه
                'expires_in': 300  # 5 دقیقه
            })
            
        except User.DoesNotExist:
            # به دلایل امنیتی، پیام یکسان برای کاربر موجود و ناموجود
            return Response({
                'message': _('If the mobile number is registered, an OTP will be sent.')
            })
        except Exception as e:
            logger.error(f"OTP request failed: {str(e)}")
            return Response({
                'error': _('Failed to send OTP.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            otp = OTPCode.objects.get(
                id=serializer.validated_data['otp_id'],
                user__mobile=serializer.validated_data['mobile'],
            )
            
            if otp.verify(serializer.validated_data['code']):
                # تایید موبایل کاربر
                otp.user.verify_mobile()
                
                # تولید توکن
                refresh = RefreshToken.for_user(otp.user)
                
                # بروزرسانی اطلاعات ورود
                AuthService.update_login_info(otp.user, request)
                
                return Response({
                    'message': _('OTP verified successfully.'),
                    'user': UserSerializer(otp.user, context={'request': request}).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
            else:
                return Response({
                    'error': _('Invalid or expired OTP.')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except OTPCode.DoesNotExist:
            return Response({
                'error': _('Invalid OTP reference.')
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"OTP verification failed: {str(e)}")
            return Response({
                'error': _('Verification failed.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
    """
    تایید موبایل کاربر
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        تایید موبایل با OTP
        """
        otp_id = request.data.get('otp_id')
        code = request.data.get('code')
        
        if not otp_id or not code:
            return Response({
                'error': _('OTP ID and code are required.')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from apps.accounts.models import OTPCode
            otp = OTPCode.objects.get(
                id=otp_id,
                user=request.user,
                purpose__in=['register', 'verify_profile'],
                is_used=False
            )
            
            if otp.verify(code):
                request.user.verify_mobile()
                
                logger.info(f"Mobile verified for user: {request.user.mobile}")
                
                return Response({
                    'message': _('Mobile verified successfully.')
                })
            else:
                return Response({
                    'error': _('Invalid or expired OTP.')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except OTPCode.DoesNotExist:
            return Response({
                'error': _('Invalid OTP reference.')
            }, status=status.HTTP_400_BAD_REQUEST)


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
                    send_otp_sms.delay(str(user.id), otp.code)
                    
                    return Response({
                        'message': _('Password reset code sent to your mobile.'),
                        'otp_id': str(otp.id),  # فقط در محیط توسعه
                        'reset_method': 'otp'
                    })
                
                elif user.email:
                    # ارسال ایمیل بازیابی
                    from apps.accounts.tasks import send_password_reset_email
                    send_password_reset_email.delay(str(user.id))
                    
                    return Response({
                        'message': _('Password reset link sent to your email.'),
                        'reset_method': 'email'
                    })
            
            # پیام یکسان برای امنیت
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
            if 'otp_id' in serializer.validated_data:
                from apps.accounts.models import OTPCode
                otp = OTPCode.objects.get(
                    id=serializer.validated_data['otp_id'],
                    user=user,
                    purpose='reset_password'
                )
                
                if not otp.verify(serializer.validated_data['code']):
                    return Response({
                        'error': _('Invalid or expired OTP.')
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # تغییر رمز عبور
            user.set_password(serializer.validated_data['new_password'])
            user.reset_failed_login()
            user.save()
            
            # باطل کردن توکن‌های قبلی
            AuthService.revoke_all_tokens(user)
            
            # تولید توکن جدید
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"Password reset completed for user: {user.email or user.mobile}")
            
            return Response({
                'message': _('Password reset successful.'),
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
            
        except OTPCode.DoesNotExist:
            return Response({
                'error': _('Invalid OTP reference.')
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Password reset confirm failed: {str(e)}")
            return Response({
                'error': _('Failed to reset password.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)