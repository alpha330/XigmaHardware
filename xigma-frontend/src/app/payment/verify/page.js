// src/app/payment/verify/page.js
import React, { Suspense } from 'react';
import VerifyClient from '../../../components/payment/VerifyClient';

export const metadata = {
  title: 'نتیجه تراکنش | XigmaHardware',
};

// نمایش یک لودینگ ساده سمت سرور تا زمانی که پارامترهای URL کلاینت خوانده شوند
const VerifyFallback = () => (
  <div style={{ textAlign: 'center', padding: '5rem', color: '#666' }}>
    <h2>در حال آماده‌سازی اطلاعات پرداخت...</h2>
  </div>
);

export default function VerifyPage() {
  return (
    <Suspense fallback={<VerifyFallback />}>
      <VerifyClient />
    </Suspense>
  );
}