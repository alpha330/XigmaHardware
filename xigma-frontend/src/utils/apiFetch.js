// src/utils/apiFetch.js
import Cookies from 'js-cookie';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let refreshTokenPromise = null;

const forceLogout = () => {
  Cookies.remove('token', { path: '/' });
  Cookies.remove('refresh', { path: '/' });
  if (typeof window !== 'undefined') {
    window.location.href = '/auth/login';
  }
};

export const apiFetch = async (endpoint, options = {}) => {
  const getAccessToken = () => Cookies.get('token');
  const getRefreshToken = () => Cookies.get('refresh');

  // 🎯 جادوی آپلود فایل همین‌جا داخل setHeaders پیاده‌سازی شده است
  const setHeaders = (token) => {
    const headers = new Headers(options.headers || {});
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    // اگر body از نوع FormData باشد، Content-Type ست نمی‌شود تا مرورگر خودش boundary بسازد
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }
    return headers;
  };

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  let response = await fetch(url, {
    ...options,
    headers: setHeaders(getAccessToken()),
  });

  if (response.status === 401) {
    const refresh = getRefreshToken();

    if (!refresh) {
      forceLogout();
      throw new Error('Session Expired');
    }

    if (!refreshTokenPromise) {
      refreshTokenPromise = fetch(`${BASE_URL}/api/v1/accounts/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      })
      .then(async (res) => {
        if (!res.ok) throw new Error('Refresh token is invalid or blacklisted');
        const data = await res.json();

        Cookies.set('token', data.access, { expires: 1 / 24, path: '/' });

        if (data.refresh) {
          Cookies.set('refresh', data.refresh, { expires: 7, path: '/' });
        }

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
      response = await fetch(url, {
        ...options,
        headers: setHeaders(newAccessToken),
      });
    } catch (error) {
      throw new Error('Failed to retry request');
    }
  }

  return response;
};