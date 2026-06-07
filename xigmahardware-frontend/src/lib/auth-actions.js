// src/lib/auth-actions.js
'use server';

import { cookies } from 'next/headers';

/**
 * ذخیره توکن‌ها و اطلاعات کاربر در Cookie (Server-Side)
 */
export async function setAuthCookies(accessToken, refreshToken, user) {
  const cookieStore = await cookies();

  // Access Token (httpOnly = secure)
  cookieStore.set('access_token', accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60, // ۱ ساعت
    path: '/',
  });

  // Refresh Token (httpOnly = secure)
  cookieStore.set('refresh_token', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // ۷ روز
    path: '/',
  });

  // User Info (غیر httpOnly - برای دسترسی کلاینت)
  if (user) {
    cookieStore.set('user_info', JSON.stringify({
      id: user.id,
      name: user.full_name || user.first_name || user.email || '',
      email: user.email || '',
      mobile: user.mobile || '',
      role: user.role || 'client',
      avatar: user.avatar_url || null,
    }), {
      httpOnly: false,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
      path: '/',
    });
  }

  return { success: true };
}

/**
 * پاک کردن کوکی‌ها (خروج کاربر)
 */
export async function clearAuthCookies() {
  const cookieStore = await cookies();

  cookieStore.delete('access_token');
  cookieStore.delete('refresh_token');
  cookieStore.delete('user_info');

  return { success: true };
}

/**
 * دریافت اطلاعات کاربر از کوکی
 */
export async function getUserFromCookies() {
  try {
    const cookieStore = await cookies();
    const userInfo = cookieStore.get('user_info')?.value;

    if (userInfo) {
      return JSON.parse(userInfo);
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * چک کردن لاگین بودن کاربر
 */
export async function isAuthenticated() {
  const cookieStore = await cookies();
  const token = cookieStore.get('access_token')?.value;
  return !!token;
}

/**
 * دریافت access token از کوکی
 */
export async function getAccessToken() {
  const cookieStore = await cookies();
  return cookieStore.get('access_token')?.value || null;
}

/**
 * middleware helper - چک مسیرهای protected
 */
export async function checkAuth() {
  const isAuth = await isAuthenticated();
  if (!isAuth) {
    return { authenticated: false, redirect: '/auth/login' };
  }

  const user = await getUserFromCookies();
  return { authenticated: true, user };
}