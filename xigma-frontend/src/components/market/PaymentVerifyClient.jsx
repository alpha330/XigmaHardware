// src/components/market/PaymentVerifyClient.jsx
'use client';

import React, { useEffect, useState } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';
import Link from 'next/link';

// ================= STYLES =================

// انیمیشن چرخش برای حالت Loading
const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const PageWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  background-color: ${({ theme }) => theme.colors.background};
  padding: 2rem;
`;

const ResultCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 3rem 2rem;
  max-width: 500px;
  width: 100%;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
`;

const IconWrapper = styled.div`
  font-size: 5rem;
  margin-bottom: 1.5rem;

  // استایل‌دهی به آیکون لودینگ
  .spinner {
    display: inline-block;
    width: 80px;
    height: 80px;
    border: 6px solid ${({ theme }) => theme.colors.border};
    border-top-color: ${({ theme }) => theme.colors.primary};
    border-radius: 50%;
    animation: ${spin} 1s linear infinite;
  }
`;

const Title = styled.h1`
  font-size: 1.8rem;
  color: ${({ theme, status }) =>
    status === 'success' ? theme.colors.success :
    status === 'error' ? theme.colors.error :
    theme.colors.textMain};
  margin-bottom: 1rem;
`;

const Message = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
`;

const DetailsBox = styled.div`
  background-color: ${({ theme }) => theme.colors.background};
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: right;
  border: 1px solid ${({ theme }) => theme.colors.border};

  div {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.8rem;
    font-size: 0.95rem;

    &:last-child { margin-bottom: 0; }

    span.label { color: ${({ theme }) => theme.colors.textMuted}; }
    span.value { font-weight: bold; color: ${({ theme }) => theme.colors.textMain}; font-family: monospace; }
  }
`;

const ActionButtons = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;

  a, button {
    width: 100%;
    padding: 1rem;
    border-radius: 8px;
    font-weight: bold;
    font-size: 1rem;
    text-align: center;
    cursor: pointer;
    transition: opacity 0.2s;
    text-decoration: none;
    border: none;
  }

  .primary {
    background-color: ${({ theme }) => theme.colors.primary};
    color: #fff;
    &:hover { opacity: 0.9; }
  }

  .secondary {
    background-color: transparent;
    color: ${({ theme }) => theme.colors.textMain};
    border: 1px solid ${({ theme }) => theme.colors.border};
    &:hover { background-color: ${({ theme }) => theme.colors.background}; }
  }
`;

export default function PaymentVerifyClient() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { showToast } = useToast();

  const [verifyState, setVerifyState] = useState('loading'); // 'loading' | 'success' | 'error'
  const [paymentData, setPaymentData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    // گرفتن پارامترهای زرین‌پال از URL
    const authority = searchParams.get('Authority');
    const status = searchParams.get('Status');

    if (!authority) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setVerifyState('error');
      setErrorMessage('اطلاعات پرداخت نامعتبر است.');
      return;
    }

    // اگر کاربر در درگاه انصراف داده باشد
    if (status === 'NOK') {
      setVerifyState('error');
      setErrorMessage('پرداخت توسط شما لغو شد یا با خطا مواجه گردید.');
      return;
    }

    // اگر Status === 'OK' بود، باید Authority را به بک‌اند بفرستیم تا تایید نهایی شود
    const verifyPayment = async () => {
      try {
        // 🎯 مسیر API بک‌اند شما برای تایید زرین‌پال
        const res = await apiFetch('/api/v1/market/payment/verify/', {
          method: 'POST',
          body: JSON.stringify({ authority: authority })
        });

        const data = await res.json();

        if (res.ok) {
          setVerifyState('success');
          setPaymentData(data); // شامل شماره پیگیری (ref_id) و مبلغ
          showToast('پرداخت با موفقیت انجام شد', 'success');
        } else {
          setVerifyState('error');
          setErrorMessage(data.error || 'خطا در تایید تراکنش در شبکه بانکی.');
          showToast('تایید تراکنش با مشکل مواجه شد', 'error');
        }
      } catch (error) {
        setVerifyState('error');
        setErrorMessage('ارتباط با سرور برقرار نشد. در صورت کسر وجه، مبلغ تا ۷۲ ساعت آینده بازمی‌گردد.');
      }
    };

    verifyPayment();
  }, [searchParams, showToast]);

  return (
    <PageWrapper>
      <ResultCard>

        {/* حالت در حال بررسی */}
        {verifyState === 'loading' && (
          <>
            <IconWrapper><div className="spinner" /></IconWrapper>
            <Title status="loading">در حال بررسی تراکنش...</Title>
            <Message>لطفاً منتظر بمانید و از رفرش کردن صفحه خودداری کنید. در حال ارتباط با شبکه بانکی هستیم.</Message>
          </>
        )}

        {/* حالت پرداخت موفق */}
        {verifyState === 'success' && (
          <>
            <IconWrapper>✅</IconWrapper>
            <Title status="success">پرداخت با موفقیت انجام شد</Title>
            <Message>سفارش شما با موفقیت ثبت شد و در صف پردازش قرار گرفت. از خرید شما سپاسگزاریم.</Message>

            {paymentData && (
              <DetailsBox>
                <div>
                  <span className="label">شماره پیگیری (Ref ID):</span>
                  <span className="value">{paymentData.ref_id || 'نامشخص'}</span>
                </div>
                <div>
                  <span className="label">شماره سفارش:</span>
                  <span className="value">{paymentData.order_id || '-'}</span>
                </div>
              </DetailsBox>
            )}

            <ActionButtons>
              <Link href="/profile/orders" className="primary">مشاهده وضعیت سفارش</Link>
              <Link href="/" className="secondary">بازگشت به صفحه اصلی</Link>
            </ActionButtons>
          </>
        )}

        {/* حالت پرداخت ناموفق */}
        {verifyState === 'error' && (
          <>
            <IconWrapper>❌</IconWrapper>
            <Title status="error">پرداخت ناموفق بود</Title>
            <Message>{errorMessage}</Message>

            <ActionButtons>
              <button onClick={() => router.push('/cart')} className="primary">تلاش مجدد برای پرداخت</button>
              <Link href="/" className="secondary">بازگشت به فروشگاه</Link>
            </ActionButtons>
          </>
        )}

      </ResultCard>
    </PageWrapper>
  );
}