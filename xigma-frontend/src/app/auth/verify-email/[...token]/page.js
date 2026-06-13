// src/app/auth/verify-email/[...token]/page.js
import VerifyEmailClient from '../../../../components/auth/VerifyEmailClient';

export const metadata = {
  title: 'تایید ایمیل | XigmaHardware',
};

export default async function VerifyEmailPage({ params }) {
  // در Next.js 15 پارامترها باید به صورت Promise دریافت (await) شوند
  const resolvedParams = await params;

  // چون از [...token] استفاده کردیم، توکن به صورت آرایه است. آن را با اسلش به هم می‌چسبانیم
  const tokenString = resolvedParams.token ? resolvedParams.token.join('/') : '';

  return <VerifyEmailClient token={tokenString} />;
}