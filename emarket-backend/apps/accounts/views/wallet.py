import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status,mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.models import Wallet, WalletTransaction
from apps.accounts.serializers.wallet import (
    WalletSerializer,
    WalletTransactionSerializer,
    WalletDepositSerializer,
    WalletWithdrawSerializer,
)
from apps.accounts.permissions import (
    IsOwner,
    IsAdminOrStaff,
    CanManageWallet,
)
from apps.accounts.services.wallet_service import WalletService

logger = logging.getLogger(__name__)


class WalletViewSet(
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):
    """
    ViewSet مدیریت کیف پول

    Actions:
    - my_wallet: کیف پول کاربر جاری
    - my_transactions: تراکنش‌های کاربر جاری
    - deposit: افزایش موجودی
    - withdraw: برداشت از موجودی
    - list: لیست کیف پول‌ها (فقط ادمین)
    - retrieve: جزئیات کیف پول (فقط ادمین)
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

    def get_permissions(self):
        if self.action in ['my_wallet', 'my_transactions', 'deposit', 'withdraw']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminOrStaff]
        else:
            permission_classes = [CanManageWallet]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        """
        نمایش کیف پول کاربر جاری
        """
        if not hasattr(request.user, 'wallet'):
            return Response({
                'error': _('Wallet not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        wallet = request.user.wallet
        balance_info = WalletService.get_balance(wallet)

        serializer = self.get_serializer(wallet)

        return Response({
            'wallet': serializer.data,
            'balance': balance_info,
            'recent_transactions': self._get_recent_transactions(wallet, 5)
        })

    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """
        نمایش تراکنش‌های کاربر جاری
        """
        if not hasattr(request.user, 'wallet'):
            return Response({
                'error': _('Wallet not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        wallet = request.user.wallet

        # فیلترها
        transaction_type = request.query_params.get('type')
        status_filter = request.query_params.get('status')

        # دریافت تراکنش‌ها
        transactions = WalletService.get_transactions(
            wallet,
            transaction_type=transaction_type,
            status=status_filter,
            limit=50
        )

        # صفحه‌بندی
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = WalletTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        """
        افزایش موجودی کیف پول
        """
        if not hasattr(request.user, 'wallet'):
            return Response({
                'error': _('Wallet not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        if not request.user.wallet.is_active:
            return Response({
                'error': _('Wallet is not active.')
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = WalletDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            transaction = WalletService.deposit(
                wallet=request.user.wallet,
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data.get('description', ''),
                reference_id=serializer.validated_data.get('reference_id', ''),
                metadata=serializer.validated_data.get('metadata', {})
            )

            logger.info(
                f"Wallet deposit: {request.user.email or request.user.mobile} "
                f"amount: {serializer.validated_data['amount']}"
            )

            return Response({
                'message': _('Deposit successful.'),
                'transaction': WalletTransactionSerializer(transaction).data,
                'new_balance': WalletService.get_balance(request.user.wallet)
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Deposit failed: {str(e)}")
            return Response({
                'error': _('Deposit failed.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """
        برداشت از کیف پول
        """
        if not hasattr(request.user, 'wallet'):
            return Response({
                'error': _('Wallet not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        if not request.user.wallet.is_active:
            return Response({
                'error': _('Wallet is not active.')
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = WalletWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            transaction = WalletService.withdraw(
                wallet=request.user.wallet,
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data.get('description', ''),
                reference_id=serializer.validated_data.get('reference_id', ''),
                metadata=serializer.validated_data.get('metadata', {})
            )

            logger.info(
                f"Wallet withdraw: {request.user.email or request.user.mobile} "
                f"amount: {serializer.validated_data['amount']}"
            )

            return Response({
                'message': _('Withdrawal successful.'),
                'transaction': WalletTransactionSerializer(transaction).data,
                'new_balance': WalletService.get_balance(request.user.wallet)
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Withdrawal failed: {str(e)}")
            return Response({
                'error': _('Withdrawal failed.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """
        انتقال وجه به کیف پول دیگر
        """
        if not hasattr(request.user, 'wallet'):
            return Response({
                'error': _('Wallet not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        target_wallet = self.get_object()

        serializer = WalletWithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            withdraw_tx, deposit_tx = WalletService.transfer(
                from_wallet=request.user.wallet,
                to_wallet=target_wallet,
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data.get('description', ''),
                reference_id=serializer.validated_data.get('reference_id', '')
            )

            logger.info(
                f"Wallet transfer: {request.user.email or request.user.mobile} -> "
                f"{target_wallet.user.email or target_wallet.user.mobile} "
                f"amount: {serializer.validated_data['amount']}"
            )

            return Response({
                'message': _('Transfer successful.'),
                'withdraw_transaction': WalletTransactionSerializer(withdraw_tx).data,
                'new_balance': WalletService.get_balance(request.user.wallet)
            })

        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Transfer failed: {str(e)}")
            return Response({
                'error': _('Transfer failed.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_recent_transactions(self, wallet, limit=5):
        """دریافت آخرین تراکنش‌ها"""
        transactions = wallet.transactions.all()[:limit]
        return WalletTransactionSerializer(transactions, many=True).data