// src/components/payment/VerifyClient.jsx
'use client';

import React, { useEffect, useState, useRef } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { apiFetch } from '../../utils/apiFetch';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 600px;
  margin: 4rem auto;
  padding: 0 2rem;
  text-align: center;
`;

const StatusCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme, status }) =>
    status === 'success' ? theme.colors.success :
    status === 'error' ? theme.colors.error : theme.colors.border};
  border-radius: 16px;
  padding: 3rem 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
`;

const IconWrapper = styled.div`
  font-size: 4rem;
  margin-bottom: 1.5rem;
  animation: ${({ status }) => status === 'loading' ? 'pulse 1.5s infinite' : 'none'};

  @keyframes pulse {
    0% { opacity: 0.5; transform: scale(0.95); }
    50% { opacity: 1; transform: scale(1.05); }
    100% { opacity: 0.5; transform: scale(0.95); }
  }
`;

const Title = styled.h1`
  font-size: 1.6rem;
  color: ${({ theme, status }) =>
    status === 'success' ? theme.colors.success :
    status === 'error' ? theme.colors.error : theme.colors.textMain};
  margin-bottom: 1rem;
`;

const Message = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
`;

const DataRow = styled.div`
  display: flex;
  justify-content: space-between;
  background-color: ${({ theme }) => theme.colors.background};
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  font-size: 0.95rem;

  .label { color: ${({ theme }) => theme.colors.textMuted}; }
  .value { font-weight: bold; color: ${({ theme }) => theme.colors.textMain}; font-family: monospace; letter-spacing: 1px; }
`;

const ActionButton = styled(Link)`
  display: inline-block;
  background-color: ${({ theme, status }) =>
    status === 'error' ? theme.colors.error : theme.colors.primary};
  color: #fff;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-weight: bold;
  text-decoration: none;
  margin-top: 1.5rem;
  transition: opacity 0.2s;

  &:hover { opacity: 0.9; }
`;

export default function VerifyClient() {
  const searchParams = useSearchParams();
  const hasFetched = useRef(false); // جلوگیری از فراخوانی دوگانه در React Strict Mode

  const [status, setStatus] = useState('loading'); // loading, success, error
  const [message, setMessage] = useState('در حال بررسی وضعیت پرداخت و ارتباط با بانک...');
  const [verifyData, setVerifyData] = useState(null);

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    const verifyPayment = async () => {
      // استخراج تمام پارامترهایی که بانک در URL فرستاده است
      const params = Object.fromEntries(searchParams.entries());

      // در درگاه‌های مختلف، شناسه تراکنش با نام‌های متفاوتی برمی‌گردد
      // پی‌پینگ معمولاً clientrefid است، زرین‌پال Authority یا درگاه‌های دیگر log_id
      const paymentLogId = params.clientrefid || params.Authority || params.log_id;

      if (!paymentLogId) {
        setStatus('error');
        setMessage('شناسه تراکنش یافت نشد. به نظر می‌رسد درخواست نامعتبر است.');
        return;
      }

      try {
        // ارسال درخواست تایید به اندپوینت verify بک‌اند شما
        const res = await apiFetch(`/api/v1/payment/verify/${paymentLogId}/`, {
          method: 'POST',
          body: JSON.stringify(params),
        });

        const data = await res.json();

        if (res.ok && data.success) {
          setStatus('success');
          setMessage(data.message || 'پرداخت شما با موفقیت تایید شد و سفارش ثبت گردید.');
          setVerifyData({
            paymentLogId: data.payment_log_id || paymentLogId,
            referenceCode: data.reference_code || params.refid || 'ثبت شده'
          });
        } else {
          setStatus('error');
          setMessage(data.error || 'پرداخت ناموفق بود یا توسط شما لغو شده است.');
          setVerifyData({ paymentLogId });
        }

      } catch (error) {
        console.error('Verify error:', error);
        setStatus('error');
        setMessage('ارتباط با سرور برقرار نشد. در صورت کسر وجه، مبلغ تا ۷۲ ساعت آینده به حساب شما بازخواهد گشت.');
      }
    };

    verifyPayment();
  }, [searchParams]);

  return (
    <PageWrapper>
      <StatusCard status={status}>

        {status === 'loading' && (
          <>
            <IconWrapper status="loading">⏳</IconWrapper>
            <Title status="loading">در حال بررسی تراکنش</Title>
            <Message>{message}</Message>
          </>
        )}

        {status === 'success' && (
          <>
            <IconWrapper status="success">✅</IconWrapper>
            <Title status="success">پرداخت موفقیت‌آمیز بود</Title>
            <Message>{message}</Message>

            {verifyData?.referenceCode && (
              <DataRow>
                <span className="label">کد پیگیری بانکی:</span>
                <span className="value">{verifyData.referenceCode}</span>
              </DataRow>
            )}

            <ActionButton href="/profile/invoices" status="success">
              مشاهده فاکتور و سفارشات
            </ActionButton>
          </>
        )}

        {status === 'error' && (
          <>
            <IconWrapper status="error">❌</IconWrapper>
            <Title status="error">پرداخت ناموفق</Title>
            <Message>{message}</Message>

            {verifyData?.paymentLogId && (
              <DataRow>
                <span className="label">شناسه خطا:</span>
                <span className="value">{verifyData.paymentLogId.split('-')[0]}</span>
              </DataRow>
            )}

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <ActionButton href="/basket/cart" status="error">
                بازگشت به سبد خرید
              </ActionButton>
            </div>
          </>
        )}

      </StatusCard>
    </PageWrapper>
  );
}