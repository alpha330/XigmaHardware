'use client';
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import apiClient from '@/utils/api';
import { showToast } from '@/components/ui/Toast';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // بررسی وجود توکن و دریافت اطلاعات کاربر در mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await apiClient.get('/accounts/me/');
        setUser(res.data);
      } catch (err) {
        // اگر توکن نامعتبر بود، آن را پاک کن
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  // تابع login با ایمیل/رمز یا موبایل/OTB (در صورت نیاز)
  const login = useCallback(async (credentials) => {
    const { email, mobile, password, otp_code } = credentials;
    const payload = {};
    if (email) payload.email = email;
    if (mobile) payload.mobile = mobile;
    if (password) payload.password = password;
    if (otp_code) payload.otp_code = otp_code;

    const res = await apiClient.post('/accounts/auth/login/', payload);
    const { tokens, user: userData } = res.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    setUser(userData);
    showToast('خوش آمدید!', 'success');
    return userData;
  }, []);

  // تابع register
  const register = useCallback(async (formData) => {
    const endpoint = formData.email
      ? '/accounts/auth/register/email/'
      : '/accounts/auth/register/mobile/';
    const res = await apiClient.post(endpoint, formData);
    const { tokens, user: userData } = res.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    setUser(userData);
    showToast('ثبت‌نام با موفقیت انجام شد', 'success');
    return userData;
  }, []);

  // تابع logout
  const logout = useCallback(async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        await apiClient.post('/accounts/auth/logout/', { refresh });
      }
    } catch (err) {
      console.warn('Logout API failed:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
      router.push('/');
      showToast('از حساب خارج شدید', 'info');
    }
  }, [router]);

  // به‌روزرسانی پروفایل کاربر
  const updateProfile = useCallback(async (data) => {
    const res = await apiClient.patch('/accounts/me/profile/', data);
    setUser(prev => ({ ...prev, ...res.data }));
    showToast('پروفایل بروزرسانی شد', 'success');
    return res.data;
  }, []);

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};