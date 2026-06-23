'use client';

import React, { useEffect, useState, useRef } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { apiFetch } from '../../utils/apiFetch';

const PageWrapper = styled.div`
  max-width: 620px;
  margin: 4rem auto;
  padding: 0 2rem;
  text-align: center;
`;

const StatusCard = styled.div`
  background-color: ${({ theme }) => theme.colors?.surface || '#fff'};
  border: 1px solid ${({ theme, status }) =>
    status === 'success' ? (theme.colors?.success || '#22c55e') :
    status === 'error' ? (theme.colors?.error || '#ef4444') :
    theme.colors?.border || '#e5e7eb'};
  border-radius: 16px;
  padding: 3rem 2.5rem;
`;

const Title = styled.h1`
  font-size: 1.7rem;
  margin-bottom: 1rem;
  color: ${({ theme, status }) =>
    status === 'success' ? (theme.colors?.success || '#22c55e') :
    status === 'error' ? (theme.colors?.error || '#ef4444') :
    theme.colors?.textPrimary || '#111827'};
`;

const Message = styled.p`
  color: ${({ theme }) => theme.colors?.textMuted || '#6b7280'};
  font-size: 1.05rem;
  line-height: 1.7;
  margin-bottom: 2rem;
`;

const Button = styled(Link)`
  display: inline-block;
  background-color: ${({ theme, variant }) =>
    variant === 'success' ? (theme.colors?.success || '#22c55e') : (theme.colors?.primary || '#3b82f6')};
  color: white;
  padding: 14px 32px;
  border-radius: 10px;
  font-weight: 600;
  text-decoration: none;
  margin-top: 1rem;
`;

export default function PaymentVerifyClient() {
  const searchParams = useSearchParams();
  const hasProcessed = useRef(false);

  const [status, setStatus] = useState('loading');
  const [message, setMessage] = useState('در حال بررسی وضعیت پرداخت...');
  const [data, setData] = useState(null);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const params = Object.fromEntries(searchParams.entries());

    // پرداخت موفق از درگاه
    if (params.Status === 'OK' || params.status === 'success') {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setStatus('verifying');
      setMessage('در حال تأیید پرداخت و شارژ کیف پول...');

      const paymentLogId = params.payment_log_id || sessionStorage.getItem('last_payment_log_id');

      if (paymentLogId) {
        // eslint-disable-next-line react-hooks/immutability
        verifyPaymentWithBackend(paymentLogId, params);
      } else {
        setStatus('success');
        setMessage('پرداخت با موفقیت انجام شد. لطفاً کیف پول را بررسی کنید.');
        setData({ refId: params.Authority || params.ref_id });
      }
      return;
    }

    if (params.status === 'error' || params.message) {
      setStatus('error');
      setMessage(params.message || 'پرداخت با خطا مواجه شد.');
      return;
    }

    setStatus('error');
    setMessage('شناسه پرداخت یافت نشد.');
  }, [searchParams]);

  // کال کردن endpoint verify بک‌اند (مهم)
  const verifyPaymentWithBackend = async (paymentLogId, params) => {
    try {
      const payload = {
        authority: params.Authority || params.authority,
        status: params.Status || params.status,
        ref_id: params.ref_id,
        amount: params.amount,
      };

      const res = await apiFetch(`/api/v1/payment/verify/${paymentLogId}/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      const result = await res.json();

      if (res.ok && result.success) {
        setStatus('success');
        setMessage('پرداخت با موفقیت انجام شد و کیف پول شارژ گردید.');
        setData({
          refId: result.reference_code || params.Authority,
          amount: params.amount,
        });
      } else {
        setStatus('error');
        setMessage(result.message || 'تأیید پرداخت با خطا مواجه شد.');
      }
    } catch (error) {
      console.error('Verify payment error:', error);
      setStatus('error');
      setMessage('خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.');
    }
  };

  return (
    <PageWrapper>
      <StatusCard status={status}>
        {(status === 'loading' || status === 'verifying') && (
          <>
            <Title status="verifying">در حال پردازش پرداخت...</Title>
            <Message>{message}</Message>
          </>
        )}

        {status === 'success' && (
          <>
            <Title status="success">پرداخت موفق بود ✓</Title>
            <Message>{message}</Message>

            {data?.amount && (
              <div style={{ marginBottom: '1.5rem', fontSize: '1.15rem' }}>
                مبلغ: <strong>{Number(data.amount).toLocaleString('fa-IR')} ریال</strong>
              </div>
            )}

            <Button href="/accounts/wallet" variant="success">
              مشاهده کیف پول
            </Button>
          </>
        )}

        {status === 'error' && (
          <>
            <Title status="error">پرداخت ناموفق</Title>
            <Message>{message}</Message>
            <Button href="/accounts/wallet" variant="error">
              بازگشت به کیف پول
            </Button>
          </>
        )}
      </StatusCard>
    </PageWrapper>
  );
}