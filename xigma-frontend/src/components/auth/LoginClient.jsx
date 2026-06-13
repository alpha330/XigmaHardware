// src/components/auth/LoginClient.jsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { AuthContainer, AuthCard, AuthTitle, AuthSubtitle, InputGroup, Label, Input, SubmitButton, BottomLink } from './AuthStyles';
import { useToast } from '../ui/ToastProvider'; // ایمپورت هوک

export default function LoginClient() {
  const router = useRouter();
  const { showToast } = useToast(); // استفاده از هوک
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/v1/accounts/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'ایمیل یا رمز عبور اشتباه است.');

      localStorage.setItem('token', data.access);
      localStorage.setItem('refresh', data.refresh);

      showToast('با موفقیت وارد شدید! خوش آمدید.', 'success'); // نمایش Toast موفقیت
      setTimeout(() => router.push('/accounts/profile'), 1500);

    } catch (error) {
      showToast(error.message, 'error'); // نمایش Toast ارور
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContainer>
      <AuthCard>
        <AuthTitle>ورود به حساب کاربری</AuthTitle>
        <AuthSubtitle>برای دسترسی به پنل کاربری و سبد خرید، وارد شوید.</AuthSubtitle>

        <form onSubmit={handleSubmit}>
          {/* تگ AlertMessage حذف شد */}
          <InputGroup>
            <Label htmlFor="email">ایمیل</Label>
            <Input id="email" type="email" dir="ltr" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
          </InputGroup>

          <InputGroup>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Label htmlFor="password">رمز عبور</Label>
              <Link href="/auth/forgot-password" style={{ fontSize: '0.8rem', color: 'var(--primary)' }}>فراموشی رمز؟</Link>
            </div>
            <Input id="password" type="password" dir="ltr" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} required />
          </InputGroup>

          <SubmitButton type="submit" disabled={loading}>
            {loading ? 'در حال ورود...' : 'ورود'}
          </SubmitButton>
        </form>

        <BottomLink>حساب کاربری ندارید؟ <Link href="/auth/register">ثبت‌نام کنید</Link></BottomLink>
      </AuthCard>
    </AuthContainer>
  );
}