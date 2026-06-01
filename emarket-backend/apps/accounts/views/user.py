import logging
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.serializers.user import (
    UserSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    UserRoleChangeSerializer,
)
from apps.accounts.permissions import (
    IsOwner,
    IsSuperAdmin,
    IsAdminOrStaff,
)
from apps.accounts.services.user_service import UserService

User = get_user_model()
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet مدیریت کاربران
    
    Actions:
    - me: دریافت و ویرایش پروفایل کاربر جاری
    - list: لیست کاربران (فقط ادمین)
    - retrieve: جزئیات کاربر (فقط ادمین)
    - update/partial_update: ویرایش کاربر (فقط ادمین)
    - delete_account: حذف حساب کاربری
    - change_role: تغییر نقش کاربر (فقط سوپر ادمین)
    - toggle_active: فعال/غیرفعال کردن کاربر (فقط ادمین)
    """
    
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """
        انتخاب سریالایزر بر اساس action
        """
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_role':
            return UserRoleChangeSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        تنظیم permissions بر اساس action
        """
        if self.action in ['me', 'delete_account']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminOrStaff]
        elif self.action in ['update', 'partial_update', 'change_role', 'toggle_active']:
            permission_classes = [IsSuperAdmin]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        دریافت یا ویرایش پروفایل کاربر جاری
        
        GET: دریافت اطلاعات کاربر
        PUT/PATCH: ویرایش اطلاعات کاربر
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response({
                'user': serializer.data,
                'profile': self._get_profile_data(request.user),
                'wallet': self._get_wallet_data(request.user),
            })
        
        # PUT یا PATCH
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            user = UserService.update_user(request.user, serializer.validated_data)
            
            logger.info(f"User updated: {user.email or user.mobile}")
            
            return Response({
                'message': _('Profile updated successfully.'),
                'user': self.get_serializer(user).data
            })
            
        except Exception as e:
            logger.error(f"User update failed: {str(e)}")
            return Response({
                'error': _('Failed to update profile.')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        """
        حذف حساب کاربری (Soft Delete)
        """
        try:
            # تایید با رمز عبور
            password = request.data.get('password')
            if not request.user.check_password(password):
                return Response({
                    'error': _('Invalid password.')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # غیرفعال کردن حساب
            request.user.is_active = False
            request.user.save()
            
            # باطل کردن توکن‌ها
            from apps.accounts.services.auth_service import AuthService
            AuthService.revoke_all_tokens(request.user)
            
            logger.info(f"User account deactivated: {request.user.email or request.user.mobile}")
            
            return Response({
                'message': _('Account deactivated successfully.')
            })
            
        except Exception as e:
            logger.error(f"Account deletion failed: {str(e)}")
            return Response({
                'error': _('Failed to delete account.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """
        لیست کاربران با فیلتر و جستجو (فقط ادمین)
        """
        try:
            # فیلترها
            queryset = User.objects.all()
            
            # فیلتر نقش
            role = request.query_params.get('role')
            if role:
                queryset = queryset.filter(role=role)
            
            # فیلتر وضعیت
            is_active = request.query_params.get('is_active')
            if is_active is not None:
                is_active = is_active.lower() == 'true'
                queryset = queryset.filter(is_active=is_active)
            
            # فیلتر تایید
            is_verified = request.query_params.get('is_verified')
            if is_verified is not None:
                is_verified = is_verified.lower() == 'true'
                if is_verified:
                    queryset = queryset.filter(is_email_verified=True) | queryset.filter(is_mobile_verified=True)
                else:
                    queryset = queryset.filter(is_email_verified=False, is_mobile_verified=False)
            
            # جستجو
            search = request.query_params.get('search')
            if search:
                from django.db.models import Q
                queryset = queryset.filter(
                    Q(email__icontains=search) |
                    Q(mobile__icontains=search) |
                    Q(profile__company_name__icontains=search)
                )
            
            # مرتب‌سازی
            ordering = request.query_params.get('ordering', '-created_at')
            queryset = queryset.order_by(ordering)
            
            # صفحه‌بندی
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"User list failed: {str(e)}")
            return Response({
                'error': _('Failed to retrieve users.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """
        تغییر نقش کاربر (فقط سوپر ادمین)
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            new_role = serializer.validated_data['role']
            user.role = new_role
            user.save()
            
            logger.info(f"User role changed: {user.email or user.mobile} -> {new_role}")
            
            return Response({
                'message': _(f'User role changed to {new_role}.'),
                'user': UserSerializer(user).data
            })
            
        except Exception as e:
            logger.error(f"Role change failed: {str(e)}")
            return Response({
                'error': _('Failed to change role.')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        فعال/غیرفعال کردن کاربر (فقط ادمین)
        """
        user = self.get_object()
        
        try:
            user.is_active = not user.is_active
            user.save()
            
            status_text = 'activated' if user.is_active else 'deactivated'
            logger.info(f"User {status_text}: {user.email or user.mobile}")
            
            return Response({
                'message': _(f'User {status_text} successfully.'),
                'is_active': user.is_active
            })
            
        except Exception as e:
            logger.error(f"Toggle active failed: {str(e)}")
            return Response({
                'error': _('Failed to update user status.')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def sellers(self, request):
        """
        لیست فروشندگان فعال
        """
        try:
            sellers = User.objects.filter(
                role='client',  # فروشنده‌ها نقش client دارند
                is_active=True,
                is_email_verified=True
            )
            
            page = self.paginate_queryset(sellers)
            if page is not None:
                serializer = UserSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = UserSerializer(sellers, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Sellers list failed: {str(e)}")
            return Response({
                'error': _('Failed to retrieve sellers.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_profile_data(self, user):
        """دریافت اطلاعات پروفایل کاربر"""
        if hasattr(user, 'profile'):
            from apps.accounts.serializers.profile import ProfileSerializer
            return ProfileSerializer(user.profile).data
        return None
    
    def _get_wallet_data(self, user):
        """دریافت اطلاعات کیف پول کاربر"""
        if hasattr(user, 'wallet'):
            from apps.accounts.serializers.wallet import WalletSerializer
            return WalletSerializer(user.wallet).data
        return None