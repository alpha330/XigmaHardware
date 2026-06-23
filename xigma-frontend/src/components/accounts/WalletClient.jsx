// src/components/accounts/WalletClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { apiFetch } from '../../utils/apiFetch';
import ToastProvider, { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 2rem;

  @media (max-width: 800px) {
    grid-template-columns: 1fr;
  }
`;

// --- Wallet Card Styles ---
const WalletCardWrapper = styled.div`
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary} 0%, ${({ theme }) => theme.colors.secondary} 100%);
  border-radius: 20px;
  padding: 2rem;
  color: #fff;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  margin-bottom: 2rem;

  &::before {
    content: ''; position: absolute; top: -50%; right: -50%;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
  }
`;

const BalanceLabel = styled.div`
  font-size: 1rem;
  opacity: 0.9;
  margin-bottom: 0.5rem;
`;

const BalanceAmount = styled.div`
  font-size: 2.5rem;
  font-weight: bold;
  letter-spacing: 1px;
  margin-bottom: 1.5rem;

  span { font-size: 1rem; font-weight: normal; margin-right: 0.5rem; }
`;

const BlockedBalance = styled.div`
  font-size: 0.9rem;
  opacity: 0.8;
  display: flex;
  justify-content: space-between;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 1rem;
`;

// --- Charge Section Styles ---
const ChargeCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
`;

const Input = styled.input`
  width: 100%;
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 1rem;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1.2rem;
  text-align: center;
  outline: none;
  margin-bottom: 1rem;
  transition: border-color 0.2s;
  &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
`;

const GatewaySelect = styled.select`
  width: 100%;
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 1rem;
  border-radius: 8px;
  font-family: inherit;
  margin-bottom: 1rem;
  outline: none;
`;

const SubmitButton = styled.button`
  width: 100%; background-color: ${({ theme }) => theme.colors.primary}; color: #fff;
  border: none; padding: 1rem; border-radius: 8px; font-weight: bold; font-size: 1.1rem;
  cursor: pointer; transition: background-color 0.2s;
  &:hover:not(:disabled) { background-color: ${({ theme }) => theme.colors.secondary}; }
  &:disabled { opacity: 0.6; cursor: not-allowed; }
`;

// --- Transactions Styles ---
const TransactionsCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
`;

const SectionTitle = styled.h3`
  font-size: 1.3rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1.5rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  padding-bottom: 0.5rem;
`;

const TransactionRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};

  &:last-child { border-bottom: none; }
`;

const TxInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
`;

const TxTitle = styled.span`
  color: ${({ theme }) => theme.colors.textMain};
  font-weight: bold;
`;

const TxDate = styled.span`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.8rem;
`;

const TxAmount = styled.div`
  font-weight: bold;
  font-size: 1.1rem;
  color: ${({ type, theme }) => type === 'deposit' || type === 'wallet_charge' ? theme.colors.success : theme.colors.error};

  &::before { content: '${({ type }) => type === 'deposit' || type === 'wallet_charge' ? '+' : '-'} '; }
`;

const TxStatus = styled.span`
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  background-color: ${({ status, theme }) =>
    status === 'verified' ? `${theme.colors.success}20` :
    status === 'pending' ? `${theme.colors.warning}20` : `${theme.colors.error}20`};
  color: ${({ status, theme }) =>
    status === 'verified' ? theme.colors.success :
    status === 'pending' ? theme.colors.warning : theme.colors.error};
`;

export default function WalletClient() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [chargeLoading, setChargeLoading] = useState(false);
  const [userData, setUserData] = useState([]);
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);

  const [gateways, setGateways] = useState([]);
  const [selectedGateway, setSelectedGateway] = useState('');
  const [chargeAmount, setChargeAmount] = useState('');

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price || 0);

  useEffect(() => {
    const fetchWalletData = async () => {
      try {
        const [walletRes, txRes, gwRes] = await Promise.all([
          apiFetch('/api/v1/accounts/wallets/my_wallet/'),
          apiFetch('/api/v1/accounts/wallets/my_transactions/'),
          apiFetch('/api/v1/payment/gateways/active_gateways/')
        ]);
        const wbalacneGeneral = await walletRes.json()
        if (walletRes.ok) setWallet(wbalacneGeneral.balance);

        if (txRes.ok) {
          const txData = await txRes.json();
          // پشتیبانی از صفحه‌بندی (Pagination) در صورت وجود
          setTransactions(txData.results || txData);
        }

        if (gwRes.ok) {
          const gwData = await gwRes.json();
          // فیلتر کردن درگاه‌های آنلاین و حذف خود کیف پول از لیست گزینه‌های شارژ
          const onlineGateways = gwData.filter(gw => gw.type !== 'wallet' && gw.supports?.online);
          setGateways(onlineGateways);
          if (onlineGateways.length > 0) setSelectedGateway(onlineGateways[0].id);
        }

      } catch (error) {
        showToast('خطا در دریافت اطلاعات کیف پول.', 'error');
      } finally {
        setLoading(false);
      }
    };
    const fetchUserData = async () => {
        try {
          const res = await apiFetch('/api/v1/accounts/users/me/');
          if (res.ok) {
            const data = await res.json();
            const user = data.user || data;
            setUserData(user);
          }
        } catch (error) {
          console.error("Failed user");
        }
      };
    fetchUserData()
    fetchWalletData();
  }, [showToast]);

  const handleChargeWallet = async (e) => {
    e.preventDefault();
    const amountNum = Number(chargeAmount);

    if (!amountNum || amountNum < 10000) {
      return showToast('حداقل مبلغ شارژ ۱۰,۰۰۰ تومان است.', 'warning');
    }
    if (!selectedGateway) {
      return showToast('لطفاً یک درگاه پرداخت انتخاب کنید.', 'warning');
    }

    setChargeLoading(true);
    try {
      // ۱. صدور فاکتور شارژ کیف پول
      const invoiceRes = await apiFetch('/api/v1/financial/invoices/wallet_charge/', {
        method: 'POST',
        body: JSON.stringify({
          user_id:userData.id,
          amount: amountNum,
          payment_method: 'online_gateway',
          description: 'شارژ آنلاین کیف پول حساب کاربری',
          extra_data: { is_wallet_charge: true }
        })
      });
      const invoiceData = await invoiceRes.json();
      if (!invoiceRes.ok) throw new Error(invoiceData.error || 'خطا در صدور فاکتور شارژ');

      // ۲. انتقال به درگاه بانکی
      const payRes = await apiFetch('/api/v1/payment/pay/', {
        method: 'POST',
        body: JSON.stringify({
          amount: amountNum,
          invoice_id: invoiceData.invoice.id,
          gateway_id: selectedGateway,
          description: "شارژ والت کاربر",
          callback_url: `${window.location.origin}/payment/verify`
        })
      });

      const payData = await payRes.json();
      if (payData.success) {
        // اگر پاسخ مستقیم به درگاه بود، کاربر را به آنجا هدایت کن
        sessionStorage.setItem('last_payment_log_id',payData.payment_log_id);
        window.location.href = payData.payment_url;
        showToast('در حال انتقال به درگاه پرداخت...', 'success');
        return;
      }else {
        showToast('درگاه پرداخت باز نشد', 'warning');
        setChargeLoading(false);
      }
    } catch (error) {
      showToast(error.message, 'error');
      setChargeLoading(false);
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', width: '100%', marginTop: '4rem' }}>در حال بارگذاری کیف پول...</h2></PageWrapper>;

  return (
    <PageWrapper>
      {/* بخش راست: موجودی و فرم شارژ */}
      <div>
        <WalletCardWrapper>
          <BalanceLabel>موجودی قابل استفاده</BalanceLabel>
          <BalanceAmount>
            {formatPrice(wallet?.available_balance || wallet?.balance)} <span>تومان</span>
          </BalanceAmount>

          <BlockedBalance>
            <span>موجودی کل: {formatPrice(wallet?.balance)} تومان</span>
            <span>مسدود شده: {formatPrice(wallet?.blocked_balance || 0)} تومان</span>
          </BlockedBalance>
        </WalletCardWrapper>

        <ChargeCard>
          <SectionTitle>افزایش موجودی</SectionTitle>
          <form onSubmit={handleChargeWallet}>
            <Input
              type="number"
              dir="ltr"
              placeholder="مبلغ به تومان (مثلاً 500000)"
              value={chargeAmount}
              onChange={(e) => setChargeAmount(e.target.value)}
            />

            <GatewaySelect value={selectedGateway} onChange={(e) => setSelectedGateway(e.target.value)}>
              {gateways.length === 0 && <option value="">درگاهی فعال نیست</option>}
              {gateways.map(gw => (
                <option key={gw.id} value={gw.id}>{gw.name}</option>
              ))}
            </GatewaySelect>

            <SubmitButton type="submit" disabled={chargeLoading || gateways.length === 0}>
              {chargeLoading ? 'در حال انتقال به درگاه...' : 'پرداخت و شارژ کیف پول'}
            </SubmitButton>
          </form>
        </ChargeCard>
      </div>

      {/* بخش چپ: لیست تراکنش‌ها */}
      <div>
        <TransactionsCard>
          <SectionTitle>تراکنش‌های اخیر من</SectionTitle>

          {transactions.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--textMuted)', padding: '2rem 0' }}>
              تاکنون هیچ تراکنشی در حساب شما ثبت نشده است.
            </p>
          ) : (
            transactions.map(tx => (
              <TransactionRow key={tx.id}>
                <TxInfo>
                  <TxTitle>{tx.description || 'تراکنش مالی'}</TxTitle>
                  <TxDate>
                    {new Date(tx.transaction_date || tx.created_at).toLocaleDateString('fa-IR', {
                      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    })}
                  </TxDate>
                  <TxStatus status={tx.status}>{tx.status_display?.label || tx.status}</TxStatus>
                </TxInfo>

                <TxAmount type={tx.transaction_type}>
                  {formatPrice(tx.amount)} تومان
                </TxAmount>
              </TransactionRow>
            ))
          )}
        </TransactionsCard>
      </div>
    </PageWrapper>
  );
}
