// src/app/payment/verify/page.js
import PaymentVerifyClient from '../../../components/market/PaymentVerifyClient';

export const metadata = {
  title: 'نتیجه پرداخت | فروشگاه',
};

// این صفحه باید Server Component باشد اما منطق بررسی در Client Component هندل می‌شود
export default function PaymentVerifyPage() {
  return <PaymentVerifyClient />;
}