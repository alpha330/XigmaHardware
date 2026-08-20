import Cookies from 'js-cookie';
import { apiUrl } from './apiUrl';
import { clearAuthTokens, storeAuthTokens } from './authCookies';

let refreshTokenPromise = null;

const forceLogout = () => {
  clearAuthTokens();
  if (typeof window !== 'undefined') {
    // جلوگیری از ریدایرکت‌های تکراری
    if (window.location.pathname !== '/auth/login') {
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- navigation hooks are unavailable in this shared utility
      window.location.href = '/auth/login';
    }
  }
};

export const apiFetch = async (endpoint, options = {}) => {
  const getAccessToken = () => Cookies.get('token');
  const getRefreshToken = () => Cookies.get('refresh');

  const setHeaders = (token) => {
    const headers = new Headers(options.headers || {});
    if (token) headers.set('Authorization', `Bearer ${token}`);
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }
    return headers;
  };

  const url = apiUrl(endpoint);

  // درخواست اولیه
  let response = await fetch(url, { ...options, headers: setHeaders(getAccessToken()) });

  // اگر توکن منقضی شده بود
  if (response.status === 401) {
    const refresh = getRefreshToken();

    if (!refresh) {
      forceLogout();
      return response; // اجازه بده خودِ فراخواننده خطا را هندل کند
    }

    // استفاده از Promise مشترک برای جلوگیری از رفرش‌های تکراری
    if (!refreshTokenPromise) {
      refreshTokenPromise = fetch(apiUrl('/api/v1/accounts/auth/token/refresh/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      })
      .then(async (res) => {
        if (!res.ok) throw new Error('Refresh failed');
        const data = await res.json();
        storeAuthTokens({
          access: data.access,
          refresh: data.refresh || refresh,
        });
        return data.access;
      })
      .catch((err) => {
        forceLogout();
        throw err;
      })
      .finally(() => {
        refreshTokenPromise = null;
      });
    }

    try {
      const newAccessToken = await refreshTokenPromise;
      // تلاش مجدد با توکن جدید
      return await fetch(url, { ...options, headers: setHeaders(newAccessToken) });
    } catch (error) {
      // اگر اینجا خطا داد، یعنی رفرش توکن هم سوخته است
      throw error;
    }
  }

  return response;
};
