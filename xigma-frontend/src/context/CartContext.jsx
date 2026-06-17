'use client';

import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { apiFetch } from '../utils/apiFetch';
import Cookies from 'js-cookie';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState(null);
  const [isCartLoading, setIsCartLoading] = useState(true);

  // استفاده از useRef برای جلوگیری از صدا زدن مجدد درخواست همزمان
  const isFetching = useRef(false);

  const fetchCart = async () => {
    // 1. اگر توکن نداریم، درخواست نزن
    if (!Cookies.get('token')) {
      setIsCartLoading(false);
      return;
    }

    // 2. اگر در حال حاضر درخواستی در جریان است، خارج شو
    if (isFetching.current) return;

    isFetching.current = true;
    try {
      const res = await apiFetch('/api/v1/basket/carts/my_cart/');
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      } else if (res.status === 401) {
        setCart(null);
      }
    } catch (error) {
      console.error('خطا در دریافت سبد خرید:', error);
    } finally {
      // فقط مقدار جاری را تغییر می‌دهیم، بدون نیاز به setState اضافی
      isFetching.current = false;
      setIsCartLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchCart();
  }, []);

  return (
    <CartContext.Provider value={{ cart, fetchCart, isCartLoading }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);