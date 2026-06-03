import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status,mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models import Profile
from apps.accounts.serializers.profile import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    ProfileSwitchToLegalSerializer,
    ProfileSwitchToIndividualSerializer,
    ProfileCompletionSerializer,
)
from apps.accounts.permissions import (
    IsOwnerOrReadOnlyForProfile,
    IsAdminOrStaff,
)
from apps.accounts.services.profile_service import ProfileService

logger = logging.getLogger(__name__)


class ProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
    ):
    """
    ViewSet مدیریت پروفایل‌ها

    Actions:
    - my_profile: دریافت و ویرایش پروفایل کاربر جاری
    - list: لیست پروفایل‌ها (فقط ادمین)
    - retrieve: جزئیات پروفایل
    - switch_to_legal: تغییر پروفایل به حقوقی
    - switch_to_individual: تغییر پروفایل به حقیقی
    - check_completion: بررسی تکمیل بودن پروفایل
    """

    queryset = Profile.objects.all()

    def get_serializer_class(self):
        if self.action == 'my_profile':
            if self.request.method in ['PUT', 'PATCH']:
                return ProfileUpdateSerializer
            return ProfileSerializer
        elif self.action == 'switch_to_legal':
            return ProfileSwitchToLegalSerializer
        elif self.action == 'switch_to_individual':
            return ProfileSwitchToIndividualSerializer
        elif self.action == 'check_completion':
            return ProfileCompletionSerializer
        return ProfileSerializer

    def get_permissions(self):
        if self.action in ['my_profile', 'switch_to_legal',
                          'switch_to_individual', 'check_completion']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['list']:
            permission_classes = [IsAdminOrStaff]
        else:
            permission_classes = [IsOwnerOrReadOnlyForProfile]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get', 'put', 'patch'])
    def my_profile(self, request):
        """
        دریافت یا ویرایش پروفایل کاربر جاری

        GET: نمایش پروفایل
        PUT/PATCH: ویرایش پروفایل
        """
        if not hasattr(request.user, 'profile'):
            return Response({
                'error': _('Profile not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        profile = request.user.profile

        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response({
                'profile': serializer.data,
                'completion_status': self._get_completion_info(profile)
            })

        # PUT یا PATCH
        serializer = ProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=request.method == 'PATCH',
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            profile = ProfileService.update_profile(profile, serializer.validated_data)

            logger.info(f"Profile updated for user: {request.user.email or request.user.mobile}")

            return Response({
                'message': _('Profile updated successfully.'),
                'profile': self.get_serializer(profile).data,
                'completion_status': self._get_completion_info(profile)
            })

        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")
            return Response({
                'error': _('Failed to update profile.')
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def switch_to_legal(self, request):
        """
        تغییر نوع پروفایل از حقیقی به حقوقی
        """
        if not hasattr(request.user, 'profile'):
            return Response({
                'error': _('Profile not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        profile = request.user.profile

        if profile.is_legal:
            return Response({
                'error': _('Profile is already legal.')
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProfileSwitchToLegalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            profile = ProfileService.switch_to_legal(
                profile=profile,
                company_name=serializer.validated_data['company_name'],
                national_id=serializer.validated_data['national_id'],
                economic_code=serializer.validated_data['economic_code'],
            )

            logger.info(f"Profile switched to legal: {request.user.email or request.user.mobile}")

            return Response({
                'message': _('Profile switched to legal successfully.'),
                'profile': ProfileSerializer(profile).data
            })

        except Exception as e:
            logger.error(f"Switch to legal failed: {str(e)}")
            return Response({
                'error': _('Failed to switch profile type.')
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def switch_to_individual(self, request):
        """
        تغییر نوع پروفایل از حقوقی به حقیقی
        """
        if not hasattr(request.user, 'profile'):
            return Response({
                'error': _('Profile not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        profile = request.user.profile

        if profile.is_individual:
            return Response({
                'error': _('Profile is already individual.')
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProfileSwitchToIndividualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            profile = ProfileService.switch_to_individual(
                profile=profile,
                national_code=serializer.validated_data['national_code'],
            )

            logger.info(f"Profile switched to individual: {request.user.email or request.user.mobile}")

            return Response({
                'message': _('Profile switched to individual successfully.'),
                'profile': ProfileSerializer(profile).data
            })

        except Exception as e:
            logger.error(f"Switch to individual failed: {str(e)}")
            return Response({
                'error': _('Failed to switch profile type.')
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def check_completion(self, request):
        """
        بررسی وضعیت تکمیل پروفایل
        """
        if not hasattr(request.user, 'profile'):
            return Response({
                'error': _('Profile not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        profile = request.user.profile

        return Response({
            'is_completed': profile.is_completed,
            'profile_type': profile.profile_type,
            'missing_fields': self._get_missing_fields(profile),
            'can_switch': self._can_switch(profile),
        })

    def _get_completion_info(self, profile):
        """اطلاعات تکمیل پروفایل"""
        return {
            'is_completed': profile.is_completed,
            'profile_type': profile.profile_type,
            'percentage': ProfileService.calculate_completion_percentage(profile),
            'missing_fields': self._get_missing_fields(profile),
        }

    def _get_missing_fields(self, profile):
        """فیلدهای تکمیل نشده"""
        missing = []

        if profile.is_individual:
            if not profile.national_code:
                missing.append('national_code')
        else:
            if not profile.company_name:
                missing.append('company_name')
            if not profile.national_id:
                missing.append('national_id')
            if not profile.economic_code:
                missing.append('economic_code')

        if not profile.address:
            missing.append('address')
        if not profile.postal_code:
            missing.append('postal_code')

        return missing

    def _can_switch(self, profile):
        """بررسی امکان تغییر نوع پروفایل"""
        if profile.is_individual:
            return {
                'can_switch_to_legal': True,
                'requirements': ['company_name', 'national_id', 'economic_code']
            }
        else:
            return {
                'can_switch_to_individual': True,
                'requirements': ['national_code']
            }