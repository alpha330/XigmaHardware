// src/app/page.js
import HomeClient from '../components/home/HomeClient';

export const revalidate = 60;

// تابع کمکی برای استخراج آرایه از ریسپانس‌های احتمالی صفحه‌بندی شده
const normalizeData = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

async function getFeaturedProducts() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/market/products/featured/', { next: { revalidate: 60 } });
    if (!res.ok) throw new Error();
    const data = await res.json();
    return normalizeData(data);
  } catch (e) {
    return [
      { id: 1, name: 'سرور HP ProLiant DL380 G10', market_price: 120000000 },
      { id: 2, name: 'سوییچ سیسکو Catalyst 2960', market_price: 15000000 },
    ];
  }
}

async function getBestsellers() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/market/products/bestsellers/', { next: { revalidate: 60 } });
    if (!res.ok) throw new Error();
    const data = await res.json();
    return normalizeData(data);
  } catch (e) {
    return [
      { id: 5, name: 'رم سرور 64GB DDR4', market_price: 12000000 },
      { id: 6, name: 'حافظه SSD 4TB NVMe', market_price: 22000000 },
    ];
  }
}

async function getArticles() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/website/articles/featured/', { next: { revalidate: 60 } });
    if (!res.ok) throw new Error();
    const data = await res.json();
    return normalizeData(data);
  } catch (e) {
    return [
      { id: 1, title: 'راهنمای خرید سرور G10', summary: 'در این مقاله به بررسی تفاوت‌های نسل‌های مختلف سرورهای HP می‌پردازیم...' },
    ];
  }
}

async function getReviews() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/market/reviews/', { next: { revalidate: 60 } });
    if (!res.ok) throw new Error();
    const data = await res.json();
    return normalizeData(data);
  } catch (e) {
    return [
      { id: 1, user_name: 'شرکت فناوران', title: 'کیفیت عالی قطعات', body: 'سرور دقیقا با کانفیگ درخواستی پلمپ به دست ما رسید. ممنون از پشتیبانی خوبتون.' },
    ];
  }
}

export default async function HomePage() {
  const [featuredProducts, bestsellers, articles, reviews] = await Promise.all([
    getFeaturedProducts(),
    getBestsellers(),
    getArticles(),
    getReviews()
  ]);

  return (
    <HomeClient
      featuredProducts={featuredProducts}
      bestsellers={bestsellers}
      articles={articles}
      reviews={reviews}
    />
  );
}