const BASE_URL = process.env.API_BASE_URL;

export async function fetchAPI(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const token = options.token || ''; // می‌توان از cookies خواند

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };

  const res = await fetch(url, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.error || `API Error: ${res.status}`);
  }

  return res.json();
}

// توابع کمکی برای SSR
export const getCategories = () => fetchAPI('/stock/categories/?root=true');
export const getBrands = () => fetchAPI('/stock/brands/');
export const getFeaturedProducts = () => fetchAPI('/market/products/featured/');
export const getNews = () => fetchAPI('/website/news/?status=published');
export const getReviews = () => fetchAPI('/market/reviews/?sort=-created_at&limit=6');