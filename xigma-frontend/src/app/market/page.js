// src/app/market/page.js
import MarketClient from '../../components/market/MarketClient';

// این صفحه چون دارای فیلترهای داینامیک است، نباید کش ثابت شود
export const dynamic = 'force-dynamic';

// تابع نرمال‌سازی برای جلوگیری از خطای map در دیتای صفحه‌بندی شده
const normalizeData = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

// دریافت محصولات با اعمال فیلترها
async function getProducts(searchParams) {
  try {
    // تبدیل آبجکت پارامترها به Query String (مثل ?category=1)
    const queryString = new URLSearchParams(searchParams).toString();
    const endpoint = queryString
      ? `http://localhost:8000/api/v1/market/products/?${queryString}`
      : `http://localhost:8000/api/v1/market/products/`;

    const res = await fetch(endpoint, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch products');

    const data = await res.json();
    return normalizeData(data);
  } catch (error) {
    console.error('Products fetch error:', error);
    // دیتای تستی برای زمانی که بک‌اند در دسترس نیست
    return [
      { id: 1, name: 'سرور HP DL380 G10', market_price: 120000000 },
      { id: 2, name: 'سوییچ سیسکو 2960', market_price: 15000000 },
      { id: 3, name: 'پردازنده Intel Core i9', market_price: 25000000 },
      { id: 4, name: 'کارت گرافیک RTX 4090', market_price: 110000000 },
    ];
  }
}

// دریافت لیست دسته‌بندی‌ها (از اندپوینتی که در داکیومنت دادید)
async function getCategories() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/stock/categories/', {
      next: { revalidate: 3600 } // دسته‌بندی‌ها دیر به دیر عوض می‌شوند
    });
    if (!res.ok) throw new Error('Failed to fetch categories');

    const data = await res.json();
    return normalizeData(data);
  } catch (error) {
    console.error('Categories fetch error:', error);
    return [
      { id: 1, name: 'سرور و تجهیزات دیتاسنتر' },
      { id: 2, name: 'تجهیزات شبکه و رادیویی' },
      { id: 3, name: 'قطعات PC و ورک‌استیشن' },
    ];
  }
}

// در Next.js 15 پارامتر searchParams یک Promise است
export default async function MarketPage({ searchParams }) {
  // استخراج پارامترهای URL برای پاس دادن به بک‌اند
  const resolvedParams = await searchParams;

  const [products, categories] = await Promise.all([
    getProducts(resolvedParams),
    getCategories()
  ]);

  return (
    <MarketClient
      products={products}
      categories={categories}
    />
  );
}