// src/app/market/products/[id]/page.js
import ProductDetailClient from '../../../../components/market/ProductDetailClient';

// تابع نرمال‌سازی برای داده‌های صفحه‌بندی شده
const normalizeData = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

async function getSingleProduct(id) {
  try {
    const res = await fetch(`http://localhost:8000/api/v1/market/products/${id}/`, {
      cache: 'no-store'
    });
    if (!res.ok) throw new Error('Product not found');
    return await res.json();
  } catch (error) {
    // دیتای تستی (Mock) برای زمانی که بک‌اند هنوز متصل نیست
    return {
      id: id,
      name: `محصول تستی ${id} (سرور/قطعه)`,
      condition: 'new',
      processor: 'Intel Xeon Gold 6248R',
      ram: '64GB DDR4',
      storage: '2TB SSD NVMe',
      market_price: 45000000,
      description: 'یک قطعه قدرتمند با بالاترین سطح پایداری مناسب برای سرورها و دیتاسنترها.',
    };
  }
}

async function getProductReviews(id) {
  try {
    const res = await fetch(`http://localhost:8000/api/v1/market/reviews/?product=${id}`, {
      cache: 'no-store'
    });
    if (!res.ok) throw new Error('Reviews not found');
    const data = await res.json();
    return normalizeData(data);
  } catch (error) {
    return [
      { id: 101, user_name: 'محمد رضایی', title: 'عالی بود', body: 'قطعه با بسته‌بندی مناسب و پلمپ ارسال شد. عملکردش دقیقا مطابق انتظار است.' },
      { id: 102, user_name: 'مدیر شبکه', title: 'ارزش خرید بالا', body: 'در مقایسه با بازار قیمت بسیار مناسبی داشت. دمای کاری در زیر بار سنگین هم عالیه.' }
    ];
  }
}

export default async function ProductPage({ params }) {
  // در Next.js 15 پارامترها باید await شوند
  const resolvedParams = await params;
  const { id } = resolvedParams;

  // دریافت همزمان اطلاعات محصول و نظرات آن
  const [product, reviews] = await Promise.all([
    getSingleProduct(id),
    getProductReviews(id)
  ]);

  return (
    <ProductDetailClient
      product={product}
      reviews={reviews}
    />
  );
}