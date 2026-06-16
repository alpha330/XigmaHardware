// src/components/shared/ProductCard.jsx
'use client';

import React, { useState,useEffect } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '@/utils/apiFetch';
import { useToast } from '../ui/ToastProvider';
import { useCart } from '@/context/CartContext';

// ================= STYLES =================
const Card = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 86, 210, 0.1);
    border-color: ${({ theme }) => theme.colors.primary};
  }

  /* 🎯 حل مشکل SWC Emotion: تارگت کردن کلاس به جای کامپوننت */
  &:hover .product-img {
    transform: scale(1.05);
  }

  a {
    text-decoration: none;
    color: inherit;
  }
`;

const ImageContainer = styled.div`
  width: 100%;
  height: 200px;
  margin-bottom: 1rem;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
`;

const ProductImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
`;

const ImagePlaceholder = styled.div`
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.background} 0%, ${({ theme }) => theme.colors.border} 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 2rem;
`;

const Badge = styled.span`
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: ${({ theme }) => theme.colors.error};
  color: #fff;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  z-index: 2;
`;

const WishlistBtn = styled.button`
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  border: none;
  border-radius: 50%;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);

  /* استفاده از data-attribute برای جلوگیری از خطای Next.js SWC */
  &[data-in-wishlist="true"] svg {
    fill: ${({ theme }) => theme.colors.error};
    stroke: ${({ theme }) => theme.colors.error};
  }

  svg {
    width: 20px;
    height: 20px;
    fill: none;
    stroke: ${({ theme }) => theme.colors.textMuted};
    stroke-width: 2px;
    transition: all 0.2s ease;
  }

  &:hover {
    transform: scale(1.1);
    background: #fff;
    svg { stroke: ${({ theme }) => theme.colors.error}; }
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Title = styled.h3`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const PriceWrapper = styled.div`
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px dashed ${({ theme }) => theme.colors.border};
`;

const PriceSection = styled.div`
  display: flex;
  flex-direction: column;
`;

const OldPrice = styled.span`
  font-size: 0.85rem;
  color: ${({ theme }) => theme.colors.textMuted};
  text-decoration: line-through;
  margin-bottom: 0.2rem;
`;

const Price = styled.span`
  font-size: 1.25rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
`;

// --- Animated Cart Controls ---
const CartControlWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;

  /* استفاده از شرط مستقیم در styled-components بدون ارسال $active به DOM */
  background-color: ${({ theme, active }) => active ? theme.colors.primary : 'transparent'};
  border: 2px solid ${({ theme }) => theme.colors.primary};
  border-radius: 25px;

  /* کپسول انیمیشنی */
  width: ${({ active }) => active ? '100px' : '40px'};
  height: 40px;
  transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
  overflow: hidden;
`;

const ActionBtn = styled.button`
  background: transparent;
  border: none;
  color: ${({ theme, active }) => active ? '#fff' : theme.colors.primary};
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover:not(:disabled) {
    background-color: rgba(255, 255, 255, 0.2);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const QtyDisplay = styled.span`
  color: #fff;
  font-weight: bold;
  font-size: 1rem;
  min-width: 20px;
  text-align: center;
`;

// ================= COMPONENT =================
export default function ProductCard({ product }) {
  const { showToast } = useToast();
  const { cart, fetchCart } = useCart();
  // 🎯 استیت‌ها برای کنترل UI و جلوگیری از اسپم (Loading)
  const [quantity, setQuantity] = useState(0);
  const [inWishlist, setInWishlist] = useState(false);
  const [isCartLoading, setIsCartLoading] = useState(false);
  const [isWishlistLoading, setIsWishlistLoading] = useState(false);
  const priceToFormat = product.final_price || product.market_price || 0;
  const formattedPrice = new Intl.NumberFormat('fa-IR').format(priceToFormat);
  const formattedOldPrice = new Intl.NumberFormat('fa-IR').format(product.market_price || 0);

  useEffect(() => {
    if (cart && cart.items) {
      // پیدا کردن این محصول خاص در لیست آیتم‌های سبد خرید
      const itemInCart = cart.items.find(i => i.product === product.stock_product_id);
      if (itemInCart) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setQuantity(itemInCart.quantity);
      } else {
        setQuantity(0);
      }
    }
  }, [cart, product.stock_product_id]);

  // === افزودن / افزایش در سبد خرید ===
  // === افزودن / افزایش در سبد خرید ===
  const handleAddOrIncrement = async (e) => {
    e.preventDefault();
    if (isCartLoading) return;

    if (quantity >= (product.available_quantity || product.market_quantity)) {
      showToast('موجودی این کالا در فروشگاه کافی نیست.', 'warning');
      return;
    }

    setIsCartLoading(true);

    const previousQuantity = quantity;
    setQuantity(prev => prev + 1);

    try {
      const res = await apiFetch('/api/v1/basket/carts/add_item/', {
        method: 'POST',
        body: JSON.stringify({
          product_id: product.stock_product_id,
          quantity: 1,
          cart_type: 'cart',
          notes: ''
        })
      });

      if (!res.ok) {
        throw new Error('خطا در ارتباط با سرور');
      }

      if (previousQuantity === 0) {
        showToast('محصول به سبد خرید اضافه شد', 'success');
      }

      // 🎯 بخش اضافه‌شده: حتماً باید کانتکست را اینجا رفرش کنیم تا item_id برای دکمه منفی در دسترس قرار بگیرد
      await fetchCart();

    } catch (error) {
      setQuantity(previousQuantity);
      showToast('خطا در افزودن به سبد خرید', 'error');
    } finally {
      setIsCartLoading(false);
    }
  };

  const handleDecrement = async (e) => {
    e.preventDefault();
    if (isCartLoading || quantity <= 0 || !cart) return;

    // ۱. پیدا کردن آیتم مورد نظر در سبد خرید برای گرفتن item_id
    const itemInCart = cart.items.find(i => i.product === product.stock_product_id);
    if (!itemInCart) return;

    setIsCartLoading(true);

    // ۲. آپدیت خوش‌بینانه UI
    const previousQuantity = quantity;
    const newQuantity = previousQuantity - 1;
    setQuantity(newQuantity);
    console.log("CARD PRODUCT :",newQuantity)
    try {
      // ۳. ارسال درخواست به اندپوینت آپدیت (با آیدی سبد و آیدی آیتم)
      const res = await apiFetch(`/api/v1/basket/carts/${cart.id}/update-item/${itemInCart.id}/`, {
        method: 'POST',
        body: JSON.stringify({
          quantity: newQuantity // اگر این عدد 0 شود، بک‌اند خودش آیتم را پاک می‌کند
        })
      });

      if (!res.ok) {
        throw new Error('خطا در ارتباط با سرور');
      }

      if (newQuantity === 0) {
        showToast('محصول از سبد خرید حذف شد', 'info');
      }

      // ۴. همگام‌سازی مجدد کانتکست با بک‌اند
      fetchCart();

    } catch (error) {
      // در صورت بروز خطا، UI را به حالت قبل برمی‌گردانیم
      setQuantity(previousQuantity);
      showToast('خطا در بروزرسانی سبد خرید', 'error');
    } finally {
      setIsCartLoading(false);
    }
  };
  // === علاقه‌مندی‌ها (Wishlist) ===
  const handleToggleWishlist = async (e) => {
    e.preventDefault();
    if (isWishlistLoading) return;

    setIsWishlistLoading(true);
    const newStatus = !inWishlist;

    // آپدیت خوش‌بینانه
    setInWishlist(newStatus);

    try {
      if (newStatus) {
        // اضافه کردن به سبد آرزوها (CartType: wishlist)
        const res = await apiFetch('/api/v1/basket/carts/add_item/', {
          method: 'POST',
          body: JSON.stringify({
            product_id: product.stock_product_id,
            quantity: 1,
            cart_type: 'wishlist',
            wishlist_name: 'لیست علاقه‌مندی‌ها'
          })
        });

        if (!res.ok) throw new Error();
        showToast('به لیست علاقه‌مندی‌ها اضافه شد ❤️', 'success');

      } else {
        // برای حذف از Wishlist هم نیازمند item_id هستیم (مشابه سبد خرید)
        showToast('از علاقه‌مندی‌ها حذف شد', 'info');
      }
    } catch (error) {
      setInWishlist(!newStatus); // بازگشت به حالت قبل در صورت خطا
      showToast('خطا در برقراری ارتباط با سرور', 'error');
    } finally {
      setIsWishlistLoading(false);
    }
  };

  return (
    <Card>
      <Link href={`/market/products/${product.slug || product.id}`}>
        <ImageContainer>
          {/* بج تخفیف */}
          {product.discount_badge && (
            <Badge>{product.discount_badge}</Badge>
          )}

          {/* 🎯 دکمه Wishlist با data-attribute برای جلوگیری از خطای Next */}
          <WishlistBtn
            data-in-wishlist={inWishlist ? "true" : "false"}
            onClick={handleToggleWishlist}
            disabled={isWishlistLoading}
            title={inWishlist ? "حذف از علاقه‌مندی‌ها" : "افزودن به علاقه‌مندی‌ها"}
          >
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
            </svg>
          </WishlistBtn>

          {/* 🎯 دادن کلاس .product-img به تگ عکس برای افکت Zoom */}
          {product.main_image ? (
            <ProductImage className="product-img" src={product.main_image} alt={product.title} loading="lazy" />
          ) : (
            <ImagePlaceholder className="product-img">📦</ImagePlaceholder>
          )}
        </ImageContainer>

        <Title>{product.title || 'محصول ناشناس'}</Title>
      </Link>

      <PriceWrapper>
        <PriceSection>
          {product.has_discount && (
            <OldPrice>{formattedOldPrice}</OldPrice>
          )}
          <Price>{formattedPrice} تومان</Price>
        </PriceSection>

        {/* 🎯 کنترلر سبد خرید (بدون خطای Boolean Attribute) */}
        <CartControlWrapper active={quantity > 0}>
          {quantity > 0 ? (
            <>
              <ActionBtn active={true} onClick={handleDecrement} disabled={isCartLoading}>-</ActionBtn>
              <QtyDisplay>{quantity}</QtyDisplay>
              <ActionBtn active={true} onClick={handleAddOrIncrement} disabled={isCartLoading}>+</ActionBtn>
            </>
          ) : (
            <ActionBtn active={false} onClick={handleAddOrIncrement} disabled={isCartLoading}>
              +
            </ActionBtn>
          )}
        </CartControlWrapper>

      </PriceWrapper>
    </Card>
  );
}