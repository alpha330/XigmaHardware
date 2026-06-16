// src/components/basket/CartClient.jsx
'use client';

import React, { useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';
import { useCart } from '@/context/CartContext';
import { useRouter } from 'next/navigation';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 2.5fr 1fr;
  gap: 2rem;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const SectionTitle = styled.h1`
  font-size: 1.8rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

// --- Cart Items Styles ---
const CartList = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
`;

const CartItemRow = styled.div`
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem 0;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  align-items: center;

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const ItemImage = styled.div`
  width: 100px;
  height: 100px;
  background-color: ${({ theme }) => theme.colors.background};
  border-radius: 12px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const ItemDetails = styled.div`
  flex: 1;
`;

const ItemTitle = styled(Link)`
  font-size: 1.1rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.4rem;
  display: block;
  transition: color 0.2s;

  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

const ItemSku = styled.div`
  font-size: 0.8rem;
  color: ${({ theme }) => theme.colors.textMuted};
  margin-bottom: 1rem;
`;

const ItemActions = styled.div`
  display: flex;
  align-items: center;
  gap: 1.5rem;
`;

const QuantitySelector = styled.div`
  display: flex;
  align-items: center;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 8px;
  overflow: hidden;

  button {
    background-color: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.textMain};
    border: none;
    width: 35px;
    height: 35px;
    cursor: pointer;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;

    &:hover:not(:disabled) { background-color: ${({ theme }) => theme.colors.border}; }
    &:disabled { opacity: 0.4; cursor: not-allowed; }
  }

  span {
    width: 40px;
    text-align: center;
    font-weight: bold;
    color: ${({ theme }) => theme.colors.textMain};
  }
`;

const DeleteBtn = styled.button`
  color: ${({ theme }) => theme.colors.error};
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.5rem;
  border-radius: 6px;

  &:hover { background-color: ${({ theme }) => `${theme.colors.error}15`}; }
`;

const ItemPrice = styled.div`
  font-weight: bold;
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.primary};
  white-space: nowrap;
`;

// --- Summary Styles ---
const SummaryCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  position: sticky;
  top: 100px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: ${({ theme, highlight }) => highlight ? theme.colors.textMain : theme.colors.textMuted};
  font-weight: ${({ highlight }) => highlight ? 'bold' : 'normal'};
  font-size: ${({ highlight }) => highlight ? '1.2rem' : '1rem'};
`;

const Divider = styled.div`
  height: 1px;
  background-color: ${({ theme }) => theme.colors.border};
  margin: 1.5rem 0;
`;

const CheckoutButton = styled.button`
  width: 100%;
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 1.2rem;
  border-radius: 10px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(:disabled) { background-color: ${({ theme }) => theme.colors.secondary}; }
  &:disabled { background-color: ${({ theme }) => theme.colors.border}; cursor: not-allowed; }
`;

// ================= COMPONENT =================
export default function CartClient() {
  const { showToast } = useToast();
  const router = useRouter();
  // 🎯 اتصال کامل به استیت سراسری سبد خرید
  const { fetchCart, cart, isCartLoading } = useCart();
  const [actionLoading, setActionLoading] = useState(null); // ID آیتمی که در حال آپدیت است

  // فرمت‌کننده قیمت
  const formatPrice = (price) => {
    return new Intl.NumberFormat('fa-IR').format(price) + ' تومان';
  };

  // بروزرسانی تعداد آیتم
  const handleUpdateQuantity = async (itemId, currentQty, change, maxAvailable) => {
    const newQty = currentQty + change;
    if (newQty < 1) return;
    if (newQty > maxAvailable) {
      return showToast(`موجودی این کالا در فروشگاه کافی نیست.`, 'warning');
    }

    setActionLoading(itemId);
    try {
      const res = await apiFetch(`/api/v1/basket/carts/${cart.id}/update-item/${itemId}/`, {
        method: 'POST',
        body: JSON.stringify({ quantity: newQty })
      });

      if (!res.ok) throw new Error();

      // 🎯 آپدیت کردن کانتکست تا عدد جدید در کل سایت منعکس شود
      await fetchCart();
    } catch (error) {
      showToast('خطا در بروزرسانی تعداد.', 'error');
    } finally {
      setActionLoading(null);
    }
  };

  // حذف آیتم از سبد
  const handleRemoveItem = async (itemId) => {
    setActionLoading(itemId);
    try {
      const res = await apiFetch(`/api/v1/basket/carts/${cart.id}/update-item/${itemId}/`, {
        method: 'POST',
        body: JSON.stringify({ quantity: 0 }) // در بک‌اند شما، تعداد صفر معادل حذف است
      });

      if (!res.ok) throw new Error();

      showToast('کالا از سبد خرید حذف شد.', 'success');

      // 🎯 گرفتن دیتای جدید از بک‌اند پس از حذف
      await fetchCart();
    } catch (error) {
      showToast('خطا در حذف کالا.', 'error');
      setActionLoading(null);
    }
  };

  // 🎯 نمایش لودینگ فقط در زمانی که کانتکست واقعاً در حال لود اطلاعات اولیه است
  if (isCartLoading) {
    return (
      <PageWrapper>
        <h2 style={{ textAlign: 'center', width: '100%', color: 'var(--textMuted)' }}>در حال بارگذاری سبد خرید...</h2>
      </PageWrapper>
    );
  }

  // اگر سبد وجود نداشت یا آیتمی در آن نبود
  if (!cart || !cart.items || cart.items.length === 0) {
    return (
      <PageWrapper style={{ display: 'block', textAlign: 'center', padding: '5rem 2rem' }}>
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🛒</div>
        <SectionTitle style={{ justifyContent: 'center' }}>سبد خرید شما خالی است</SectionTitle>
        <p style={{ color: 'var(--textMuted)', marginBottom: '2rem' }}>هنوز هیچ کالایی برای خرید انتخاب نکرده‌اید.</p>
        <Link href="/market" style={{ backgroundColor: 'var(--primary)', color: '#fff', padding: '0.8rem 2rem', borderRadius: '8px', fontWeight: 'bold' }}>
          مشاهده فروشگاه
        </Link>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      {/* بخش راست: لیست کالاها */}
      <div>
        <SectionTitle>🛒 سبد خرید شما</SectionTitle>
        <CartList>
          {cart.items.map(item => (
            <CartItemRow key={item.id}>
              <ItemImage>
                {item.product_image ? <img src={item.product_image} alt={item.product_name} /> : '📦'}
              </ItemImage>

              <ItemDetails>
                {/* 🎯 لینک به محصول بر اساس استایل و آدرس‌دهی پروژه شما */}
                <ItemTitle href={`/market/products/${item.product}`}>{item.product_name}</ItemTitle>
                <ItemSku>کد کالا: {item.product_sku}</ItemSku>

                {!item.is_available && (
                  <span style={{ color: 'var(--error)', fontSize: '0.8rem', backgroundColor: 'var(--error)20', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                    این کالا دیگر موجود نیست
                  </span>
                )}

                <ItemActions>
                  {/* انتخابگر تعداد */}
                  <QuantitySelector>
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity, 1, item.market_available)}
                      disabled={!item.is_available || actionLoading === item.id || item.quantity >= item.market_available}
                    >+</button>
                    <span>{actionLoading === item.id ? '...' : item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity, -1, item.market_available)}
                      disabled={!item.is_available || actionLoading === item.id || item.quantity <= 1}
                    >-</button>
                  </QuantitySelector>

                  {/* دکمه حذف */}
                  <DeleteBtn onClick={() => handleRemoveItem(item.id)} disabled={actionLoading === item.id}>
                    🗑️ حذف
                  </DeleteBtn>
                </ItemActions>
              </ItemDetails>

              <ItemPrice>
                {formatPrice(item.total_price)}
              </ItemPrice>
            </CartItemRow>
          ))}
        </CartList>
      </div>

      {/* بخش چپ: خلاصه مالی و پرداخت */}
      <div>
        <SummaryCard>
          <h3 style={{ marginBottom: '1.5rem', color: 'var(--textMain)' }}>خلاصه سفارش</h3>

          <SummaryRow>
            <span>تعداد کل اقلام:</span>
            <span>{cart.total_quantity} عدد</span>
          </SummaryRow>

          <SummaryRow>
            <span>مبلغ سفارش (بدون تخفیف):</span>
            <span>{formatPrice(cart.subtotal)}</span>
          </SummaryRow>

          {cart.discount_info?.has_discount && (
            <SummaryRow style={{ color: 'var(--success)' }}>
              <span>تخفیف اعمال شده:</span>
              <span>- {formatPrice(cart.discount_total)}</span>
            </SummaryRow>
          )}

          <Divider />

          <SummaryRow highlight>
            <span>مبلغ قابل پرداخت:</span>
            <span style={{ color: 'var(--primary)' }}>{formatPrice(cart.grand_total)}</span>
          </SummaryRow>

          {/* اگر کالای ناموجودی در سبد باشد، اجازه پرداخت نمی‌دهیم */}
          <CheckoutButton
            disabled={!cart.can_checkout}
            onClick={() => router.push('/basket/checkout')} /* 🎯 هدایت به صفحه پرداخت */
          >
            {cart.can_checkout ? 'تایید و ادامه فرآیند خرید' : 'سبد خرید نیازمند اصلاح است'}
          </CheckoutButton>

        </SummaryCard>
      </div>
    </PageWrapper>
  );
}