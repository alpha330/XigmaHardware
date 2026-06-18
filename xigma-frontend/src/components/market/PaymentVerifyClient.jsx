// src/components/market/PaymentVerifyClient.jsx
'use client';

import React, { useEffect, useState, useRef } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

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
    status === 'error' ? theme.colors.error : theme.colors.border};
  border-radius: 16px;
  padding: 3rem 2.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
`;

const Icon = styled.div`
  font-size: 4.5rem;
  margin-bottom: 1.5rem;
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

const InfoBox = styled.div`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 10px;
  padding: 1.2rem;
  margin-bottom: 1.5rem;
  text-align: left;
  font-size: 0.95rem;

  .row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.6rem;
  }
  .label { color: ${({ theme }) => theme.colors.textMuted}; }
  .value { font-weight: 600; color: ${({ theme }) => theme.colors.textMain}; font-family: monospace; }
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
  transition: all 0.2s;

  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
  }
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

    // === تشخیص قوی وضعیت از URL ===
    const isSuccess =
      params.status === 'success' ||
      params.Status === 'OK' ||
      params.status === 'success';

    const isError = params.status === 'error' || params.message;

    if (isSuccess || isError) {
      if (isSuccess) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setStatus('success');
        setMessage('پرداخت با موفقیت انجام شد و کیف پول شارژ گردید.');
        setData({
          refId: params.ref_id || params.Authority,
          paymentLogId: params.payment_log_id,
          amount: params.amount,
        });
      } else {
        setStatus('error');
        setMessage(
          params.message === 'verify_failed'
            ? 'تایید پرداخت توسط درگاه ناموفق بود.'
            : params.message || 'پرداخت با خطا مواجه شد.'
        );
        setData({ paymentLogId: params.payment_log_id });
      }
      return;
    }

    // === حالت قدیمی (فقط اگر هیچ status در URL نبود) ===
    const paymentLogId = params.clientrefid || params.Authority || params.log_id || params.payment_log_id;

    if (!paymentLogId) {
      setStatus('error');
      setMessage('شناسه تراکنش یافت نشد.');
      return;
    }

    // در این حالت چون ممکنه پاسخ JSON نباشد، فعلاً غیرفعال می‌کنیم
    setStatus('error');
    setMessage('لطفاً صفحه را رفرش کنید یا دوباره تلاش کنید.');
  }, [searchParams]);

  return (
    <PageWrapper>
      <StatusCard status={status}>

        {status === 'loading' && (
          <>
            <Icon>⏳</Icon>
            <Title status="loading">در حال بررسی تراکنش...</Title>
            <Message>{message}</Message>
          </>
        )}

        {status === 'success' && (
          <>
            <Icon>✅</Icon>
            <Title status="success">پرداخت موفق بود</Title>
            <Message>{message}</Message>

            {data && (
              <InfoBox>
                {data.refId && (
                  <div className="row">
                    <span className="label">کد پیگیری:</span>
                    <span className="value">{data.refId}</span>
                  </div>
                )}
                {data.amount && (
                  <div className="row">
                    <span className="label">مبلغ شارژ شده:</span>
                    <span className="value">{Number(data.amount).toLocaleString()} ریال</span>
                  </div>
                )}
              </InfoBox>
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

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button href="/basket/cart" variant="error">
                بازگشت به سبد خرید
              </Button>
              <Button href="/accounts/wallet" variant="error">
                مشاهده کیف پول
              </Button>
            </div>
          </>
        )}

      </StatusCard>
    </PageWrapper>
  );
}
