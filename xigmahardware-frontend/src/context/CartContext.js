'use client';
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient from '@/utils/api';
import { showToast } from '@/components/ui/Toast';
import { useAuth } from './AuthContext';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const { isAuthenticated } = useAuth();

  // دریافت اطلاعات سبد خرید (فقط در صورت احراز هویت)
  const fetchCart = useCallback(async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const res = await apiClient.get('/basket/carts/my_cart/');
      setCart(res.data);
    } catch (err) {
      console.error('Cart fetch error:', err);
      setCart(null);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // با تغییر وضعیت احراز هویت، سبد را مجدداً بارگذاری کن
  useEffect(() => {
    if (isAuthenticated) {
      fetchCart();
    } else {
      setCart(null);
    }
  }, [isAuthenticated, fetchCart]);

  // افزودن محصول به سبد
  const addToCart = useCallback(async (productId, quantity = 1) => {
    if (!isAuthenticated) {
      showToast('لطفاً ابتدا وارد شوید', 'warning');
      return;
    }
    try {
      await apiClient.post('/basket/carts/add_item/', {
        product_id: productId,
        quantity,
        cart_type: 'cart',
      });
      await fetchCart();
      showToast('به سبد خرید اضافه شد', 'success');
    } catch (err) {
      const message = err.response?.data?.error || 'خطا در افزودن به سبد';
      showToast(message, 'error');
    }
  }, [isAuthenticated, fetchCart]);

  // بروزرسانی تعداد یک آیتم
  const updateQuantity = useCallback(async (itemId, quantity) => {
    if (!cart) return;
    try {
      await apiClient.post(`/basket/carts/${cart.id}/update-item/${itemId}/`, { quantity });
      await fetchCart();
    } catch (err) {
      showToast('خطا در بروزرسانی تعداد', 'error');
    }
  }, [cart, fetchCart]);

  // حذف یک آیتم
  const removeItem = useCallback(async (itemId) => {
    if (!cart) return;
    try {
      await apiClient.post(`/basket/carts/${cart.id}/remove-item/${itemId}/`);
      await fetchCart();
      showToast('محصول از سبد حذف شد', 'info');
    } catch (err) {
      showToast('خطا در حذف محصول', 'error');
    }
  }, [cart, fetchCart]);

  // حذف انتخاب شده‌ها
  const removeSelected = useCallback(async (itemIds) => {
    if (!cart || !itemIds?.length) return;
    try {
      await apiClient.post(`/basket/carts/${cart.id}/remove_selected/`, { item_ids: itemIds });
      await fetchCart();
      showToast('محصولات انتخاب شده حذف شدند', 'info');
    } catch (err) {
      showToast('خطا در حذف', 'error');
    }
  }, [cart, fetchCart]);

  // خالی کردن سبد
  const clearCart = useCallback(async () => {
    if (!cart) return;
    try {
      await apiClient.post(`/basket/carts/${cart.id}/clear_cart/`);
      await fetchCart();
      showToast('سبد خرید خالی شد', 'info');
    } catch (err) {
      showToast('خطا در خالی کردن سبد', 'error');
    }
  }, [cart, fetchCart]);

  const value = {
    cart,
    loading,
    addToCart,
    updateQuantity,
    removeItem,
    removeSelected,
    clearCart,
    fetchCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};