// src/app/news/page.js
import NewsClient from '../../components/website/NewsClient';

// کش کردن صفحه برای یک ساعت (چون اخبار و مقالات ثانیه‌ای تغییر نمی‌کنند)
export const revalidate = 3600;

// تابع کمکی برای استخراج آرایه
const normalizeData = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

async function getArticles() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/website/articles/', {
      next: { revalidate: 3600 }
    });
    if (!res.ok) throw new Error('Failed to fetch articles');
    const data = await res.json();
    return normalizeData(data);
  } catch (error) {
    console.error('Articles fetch error:', error);
    return [
      { id: 1, title: 'راهنمای جامع خرید سرورهای HP نسل 10', summary: 'در این مقاله به بررسی تفاوت‌های سخت‌افزاری و کاربردهای سرورهای پرطرفدار اچ‌پی می‌پردازیم.' },
      { id: 2, title: 'تفاوت SSD های NVMe و SATA در سرور', summary: 'کدام حافظه برای دیتابیس‌های سنگین مناسب‌تر است؟ بررسی بنچمارک‌ها و سرعت واقعی.' },
      { id: 3, title: 'چگونه یک ورک‌استیشن رندرینگ اسمبل کنیم؟', summary: 'معرفی بهترین قطعات برای پردازش‌های سه‌بعدی و هوش مصنوعی در سال جدید.' }
    ];
  }
}

async function getNews() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/website/news/', {
      next: { revalidate: 3600 }
    });
    if (!res.ok) throw new Error('Failed to fetch news');
    const data = await res.json();
    return normalizeData(data);
  } catch (error) {
    console.error('News fetch error:', error);
    return [
      { id: 101, title: 'نسل جدید پردازنده‌های اینتل موجود شد', summary: 'پردازنده‌های سری Core Ultra هم‌اکنون با گارانتی اصلی در XigmaHardware قابل سفارش هستند.' },
      { id: 102, title: 'افتتاح شعبه جدید خدمات پس از فروش', summary: 'برای رفاه حال مشتریان سازمانی، مرکز پشتیبانی تخصصی سرورهای ما در غرب تهران راه‌اندازی شد.' }
    ];
  }
}

// تنظیمات سئو برای مجله
export const metadata = {
  title: 'اخبار و مقالات تخصصی سخت‌افزار | XigmaHardware',
  description: 'به‌روزترین اخبار دنیای آی‌تی، قطعات کامپیوتر، سرور و مقالات آموزشی تخصصی شبکه.',
};

export default async function NewsPage() {
  // استفاده از Promise.all برای اجرای همزمان درخواست‌ها و لود بسیار سریع‌تر
  const [articles, news] = await Promise.all([
    getArticles(),
    getNews()
  ]);

  return (
    <NewsClient
      articles={articles}
      news={news}
    />
  );
}