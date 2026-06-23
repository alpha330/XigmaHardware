// src/app/market/page.js
import MarketClient from '../../components/market/MarketClient';
import { apiFetch } from '../../utils/apiFetch';

// این صفحه دارای فیلترهای داینامیک است، نباید کش شود
export const dynamic = 'force-dynamic';

const normalizeData = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

async function getProducts(searchParams) {
  try {
    const queryString = new URLSearchParams(searchParams).toString();
    const endpoint = queryString
      ? `/api/v1/market/products/?${queryString}`
      : `/api/v1/market/products/`;

    const res = await apiFetch(endpoint, { cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to fetch products');
    const data = await res.json();
    return normalizeData(data);
  } catch (error) {
    console.error('Products fetch error:', error);
    return [
      { id: 1, name: 'سرور HP DL380 G10', market_price: 120000000 },
      { id: 2, name: 'سویچ سیسکو 2960', market_price: 15000000 },
      { id: 3, name: 'پردازنده Intel Core i9', market_price: 25000000 },
      { id: 4, name: 'کارت گرافیک RTX 4090', market_price: 110000000 },
    ];
  }
}

async function getCategories() {
  try {
    const res = await apiFetch('/api/v1/stock/categories/', {
      next: { revalidate: 3600 }
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

async function getBrands() {
  try {
    const res = await apiFetch('/api/v1/stock/brands/?is_active=true', {
      next: { revalidate: 3600 }
    });
    if (!res.ok) throw new Error('Failed to fetch brands');
    const data = await res.json();
    return normalizeData(data);
  } catch (error) {
    console.error('Brands fetch error:', error);
    return [];
  }
}

export default async function MarketPage({ searchParams }) {
  const resolvedParams = await searchParams;

  const [products, categories, brands] = await Promise.all([
    getProducts(resolvedParams),
    getCategories(),
    getBrands()
  ]);

  return (
    <MarketClient
      products={products}
      categories={categories}
      brands={brands}
    />
  );
}
