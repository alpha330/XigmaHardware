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
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme, status }) =>
    status === 'success' ? theme.colors.success :
    status === 'error' ? theme.colors.error :
    status === 'verifying' ? theme.colors.primary : theme.colors.border};
  border-radius: 16px;
  padding: 3rem 2.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
`;

const Icon = styled.div`
  font-size: 4.5rem;
  margin-bottom: 1.5rem;
  animation: ${({ status }) => status === 'verifying' ? 'spin 1.2s linear infinite' : 'none'};
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const Title = styled.h1`
  font-size: 1.7rem;
  margin-bottom: 1rem;
  color: ${({ theme, status }) =>
    status === 'success' ? theme.colors.success :
    status === 'error' ? theme.colors.error : theme.colors.textMain};
`;

const Message = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 1.05rem;
  line-height: 1.7;
  margin-bottom: 2rem;
`;

const Button = styled(Link)`
  display: inline-block;
  background-color: ${({ theme, variant }) =>
    variant === 'success' ? theme.colors.success : theme.colors.primary};
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

    if (params.Status === 'OK') {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setStatus('verifying');
      setMessage('در حال تایید پرداخت و شارژ کیف پول...');

      let paymentLogId = params.payment_log_id || sessionStorage.getItem('last_payment_log_id');
      console.log("PAYMENY ID :",paymentLogId)
      if (paymentLogId) {
        // فقط وضعیت را چک کن (callback را کال نکن)
        // eslint-disable-next-line react-hooks/immutability
        checkWalletStatus(paymentLogId, params);
      } else {
        setTimeout(() => {
          setStatus('success');
          setMessage('پرداخت در درگاه موفق بود. لطفاً وضعیت کیف پول را بررسی کنید.');
          setData({ refId: params.Authority });
        }, 2000);
      }
      return;
    }

    if (params.status === 'error' || params.message) {
      setStatus('error');
      setMessage(params.message || 'پرداخت با خطا مواجه شد.');
      return;
    }

    setStatus('error');
    setMessage('شناسه تراکنش یافت نشد.');
  }, [searchParams]);

  // کال کردن callback بک‌اند
  const triggerBackendCallback = async (paymentLogId, params) => {
    try {
      // کال کردن callback بک‌اند
      const callBack = await apiFetch(`/api/v1/payment/callback/${paymentLogId}/`,{method: 'GET',});
      console.log(callBack)
      // بعد از کال کردن callback، وضعیت را چک می‌کنیم
    } catch (error) {
      console.error('Callback error:', error);
      setStatus('success');
      setMessage('پرداخت در درگاه موفق بود. وضعیت کیف پول را از صفحه والت بررسی کنید.');
      setData({ refId: params.Authority });
    }
  };

  const checkWalletStatus = async (paymentLogId, params) => {
    try {
      const res = await apiFetch(`/api/v1/payment/status/${paymentLogId}/`);
      const result = await res.json();
      if (result.status === "redirected") {
        setStatus('success');
        setMessage('پرداخت با موفقیت انجام شد و کیف پول شارژ گردید.');
        setData({
          refId: params.Authority,
          paymentLogId: paymentLogId,
          amount: params.amount,
        });
        triggerBackendCallback(paymentLogId,params)
      } else {
        // هنوز شارژ نشده، دوباره چک کن
        setTimeout(() => checkWalletStatus(paymentLogId, params), 2000);
      }
    } catch (error) {
      setStatus('success');
      setMessage('پرداخت در درگاه موفق بود. وضعیت کیف پول را از صفحه والت بررسی کنید.');
    }
  };

  return (
    <PageWrapper>
      <StatusCard status={status}>
        {(status === 'loading' || status === 'verifying') && (
          <>
            <Icon status={status}>⏳</Icon>
            <Title status="verifying">در حال پردازش...</Title>
            <Message>{message}</Message>
          </>
        )}

        {status === 'success' && (
          <>
            <Icon>✅</Icon>
            <Title status="success">پرداخت موفق بود</Title>
            <Message>{message}</Message>

            {data && data.amount && (
              <div style={{ marginBottom: '1.5rem', fontSize: '1.1rem' }}>
                مبلغ: <strong>{Number(data.amount).toLocaleString()} ریال</strong>
              </div>
            )}

            <Button href="/accounts/wallet" variant="success">
              مشاهده کیف پول
            </Button>
          </>
        )}

        {status === 'error' && (
          <>
            <Icon>❌</Icon>
            <Title status="error">پرداخت ناموفق</Title>
            <Message>{message}</Message>
            <Button href="/accounts/wallet" variant="error">
              مشاهده کیف پول
            </Button>
          </>
        )}
      </StatusCard>
    </PageWrapper>
  );
}