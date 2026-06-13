// src/app/expert-reviews/page.js
import ExpertReviewsClient from '../../components/website/ExpertReviewsClient';

export const revalidate = 3600;

const normalizeData = (data) => Array.isArray(data) ? data : (data?.results || []);

async function getExpertReviews() {
  try {
    // فرض می‌کنیم در بک‌اند مقالات بررسی تخصصی با یک کوئری خاص جدا می‌شوند
    const res = await fetch('http://localhost:8000/api/v1/website/articles/?category=expert-review', {
      next: { revalidate: 3600 }
    });
    if (!res.ok) throw new Error();
    return normalizeData(await res.json());
  } catch (error) {
    return [
      { id: 1, title: 'بررسی تخصصی سرور HP DL380 G10', summary: 'در این تست، سرور را زیر بار پردازش‌های دیتابیس بردیم...', expert_score: 9.2 },
      { id: 2, title: 'تست رندرینگ با کارت گرافیک RTX 4090', summary: 'عملکرد این هیولای گرافیکی در نرم‌افزارهای 3D و دمای کاری آن...', expert_score: 9.8 },
      { id: 3, title: 'بررسی سوئیچ سیسکو سری Catalyst', summary: 'پایداری شبکه در شرکت‌های بزرگ نیازمند تجهیزات قابل اعتماد است...', expert_score: 8.9 },
    ];
  }
}

export const metadata = {
  title: 'لابراتوار تخصصی | XigmaHardware',
  description: 'نقد و بررسی تخصصی قطعات کامپیوتر و تجهیزات سرور توسط کارشناسان زیگما سخت‌افزار.',
};

export default async function ExpertReviewsPage() {
  const reviews = await getExpertReviews();
  return <ExpertReviewsClient reviews={reviews} />;
}