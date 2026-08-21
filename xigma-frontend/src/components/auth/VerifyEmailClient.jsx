// src/components/auth/VerifyEmailClient.jsx
'use client';

import React, { useEffect, useState, useRef } from 'react';
import {
  AuthContainer, AuthCard, AuthTitle, AuthSubtitle, AuthActionLink, StatusIcon
} from './AuthStyles';
import { useToast } from '../ui/ToastProvider';
import { apiFetch } from '../../utils/apiFetch';

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
        const res = await apiFetch(`/api/v1/accounts/auth/verify/email/${token}/`, {
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
            <StatusIcon data-status="loading">⏳</StatusIcon>
          </>
        )}

        {status === 'success' && (
          <>
            <AuthSubtitle>
              حساب کاربری شما با موفقیت فعال شد.
            </AuthSubtitle>
            <StatusIcon data-status="success">✅</StatusIcon>
            <AuthActionLink href="/auth/login">ورود به حساب کاربری</AuthActionLink>
          </>
        )}

        {status === 'error' && (
          <>
            <AuthSubtitle>
              متاسفانه تایید ایمیل با خطا مواجه شد. ممکن است لینک منقضی شده باشد.
            </AuthSubtitle>
            <StatusIcon data-status="error">❌</StatusIcon>
            <AuthActionLink href="/auth/login" data-variant="secondary">بازگشت به صفحه ورود</AuthActionLink>
          </>
        )}
      </AuthCard>
    </AuthContainer>
  );
}
