// src/app/market/page.js
import MarketClient from '../../components/market/MarketClient';
import { apiFetch } from '../../utils/apiFetch';

export const dynamic = 'force-dynamic';

const normalizePaginated = (data) => {
  if (!data) return { results: [], count: 0, next: null, previous: null };
  if (Array.isArray(data)) return { results: data, count: data.length, next: null, previous: null };
  return {
    results: Array.isArray(data.results) ? data.results : [],
    count: data.count || 0,
    next: data.next || null,
    previous: data.previous || null,
  };
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
    return normalizePaginated(data);
  } catch (error) {
    console.error('Products fetch error:', error);
    return {
      results: [
        { id: 1, name: 'سرور HP DL380 G10', market_price: 120000000 },
        { id: 2, name: 'سویچ سیسکو 2960', market_price: 15000000 },
        { id: 3, name: 'پردازنده Intel Core i9', market_price: 25000000 },
        { id: 4, name: 'کارت گرافیک RTX 4090', market_price: 110000000 },
      ],
      count: 4,
      next: null,
      previous: null,
    };
  }
}

async function getCategories() {
  try {
    const res = await apiFetch('/api/v1/stock/categories/', { next: { revalidate: 3600 } });
    if (!res.ok) throw new Error('Failed to fetch categories');
    const data = await res.json();
    return Array.isArray(data) ? data : (data.results || []);
  } catch (error) {
    console.error('Categories fetch error:', error);
    return [];
  }
}

async function getBrands() {
  try {
    const res = await apiFetch('/api/v1/stock/brands/?is_active=true', { next: { revalidate: 3600 } });
    if (!res.ok) throw new Error('Failed to fetch brands');
    const data = await res.json();
    return Array.isArray(data) ? data : (data.results || []);
  } catch (error) {
    console.error('Brands fetch error:', error);
    return [];
  }
}

export default async function MarketPage({ searchParams }) {
  const resolvedParams = await searchParams;
  const currentPage = parseInt(resolvedParams.page) || 1;

  const [productData, categories, brands] = await Promise.all([
    getProducts(resolvedParams),
    getCategories(),
    getBrands()
  ]);

  const totalPages = Math.ceil((productData.count || 0) / 20); // PAGE_SIZE = 20

  return (
    <MarketClient
      products={productData.results}
      categories={categories}
      brands={brands}
      pagination={{
        count: productData.count,
        currentPage,
        totalPages,
        hasPrevious: !!productData.previous,
        hasNext: !!productData.next,
      }}
    />
  );
}
