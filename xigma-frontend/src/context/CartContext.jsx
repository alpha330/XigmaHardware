// src/context/CartContext.jsx
'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiFetch } from '../utils/apiFetch';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState(null);
  const [isCartLoading, setIsCartLoading] = useState(true);

  const fetchCart = async () => {
    try {
      // 🎯 گرفتن سبد خرید فعال کاربر بر اساس API بک‌اند شما
      const res = await apiFetch('/api/v1/basket/carts/my_cart/');
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (error) {
      console.error('خطا در دریافت سبد خرید:', error);
    } finally {
      setIsCartLoading(false);
    }
  };

  // در زمان لود شدن اولیه سایت، سبد را می‌خوانیم
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

// هوک سفارشی برای استفاده راحت‌تر در بقیه کامپوننت‌ها
export const useCart = () => useContext(CartContext);