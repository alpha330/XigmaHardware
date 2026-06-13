// src/components/auth/VerifyEmailClient.jsx
'use client';

import React, { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import {
  AuthContainer, AuthCard, AuthTitle, AuthSubtitle, SubmitButton
} from './AuthStyles';
import { useToast } from '../ui/ToastProvider';

export default function VerifyEmailClient({ token }) {
  const { showToast } = useToast();
  const [status, setStatus] = useState('loading'); // 'loading' | 'success' | 'error'
  const hasRequested = useRef(false); // جلوگیری از دو بار اجرا شدن در React Strict Mode

  useEffect(() => {
    // جلوگیری از ارسال درخواست تکراری
    if (hasRequested.current) return;
    hasRequested.current = true;

    const verifyEmail = async () => {
      try {
        // ارسال درخواست GET (یا POST بسته به تنظیمات Django) به بک‌اند
        // معمولاً لینک‌های تایید ایمیل در جنگو با GET کار می‌کنند
        const res = await fetch(`http://localhost:8000/api/v1/accounts/auth/verify/email/${token}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.detail || 'لینک تایید نامعتبر است یا منقضی شده.');
        }

        setStatus('success');
        showToast('ایمیل شما با موفقیت تایید شد.', 'success');

      } catch (error) {
        setStatus('error');
        showToast(error.message, 'error');
      }
    };

    if (token) {
      verifyEmail();
    } else {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setStatus('error');
    }
  }, [token, showToast]);

  return (
    <AuthContainer>
      <AuthCard style={{ textAlign: 'center' }}>
        <AuthTitle>تایید حساب کاربری</AuthTitle>

        {status === 'loading' && (
          <>
            <AuthSubtitle>در حال بررسی و تایید ایمیل شما، لطفا منتظر بمانید...</AuthSubtitle>
            <div style={{ margin: '2rem 0', fontSize: '2rem' }}>⏳</div>
          </>
        )}

        {status === 'success' && (
          <>
            <AuthSubtitle style={{ color: 'var(--success)' }}>
              حساب کاربری شما با موفقیت فعال شد.
            </AuthSubtitle>
            <div style={{ margin: '2rem 0', fontSize: '3rem' }}>✅</div>
            <Link href="/auth/login" style={{ width: '100%', display: 'block' }}>
              <SubmitButton type="button">
                ورود به حساب کاربری
              </SubmitButton>
            </Link>
          </>
        )}

        {status === 'error' && (
          <>
            <AuthSubtitle style={{ color: 'var(--error)' }}>
              متاسفانه تایید ایمیل با خطا مواجه شد. ممکن است لینک منقضی شده باشد.
            </AuthSubtitle>
            <div style={{ margin: '2rem 0', fontSize: '3rem' }}>❌</div>
            <Link href="/auth/login" style={{ width: '100%', display: 'block' }}>
              <SubmitButton type="button" style={{ backgroundColor: 'var(--border)', color: 'var(--textMain)' }}>
                بازگشت به صفحه ورود
              </SubmitButton>
            </Link>
          </>
        )}
      </AuthCard>
    </AuthContainer>
  );
}