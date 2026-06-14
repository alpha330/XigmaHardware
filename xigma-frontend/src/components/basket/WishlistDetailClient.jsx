// src/components/basket/WishlistDetailClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

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

const BackLink = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.9rem;
  margin-bottom: 1rem;
  text-decoration: none;
  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

const InfoCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
  margin-bottom: 2rem;
`;

const WishlistTitle = styled.h1`
  font-size: 1.8rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
`;

const Description = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 0;
`;

const ItemsList = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
`;

const ItemRow = styled.div`
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
  width: 90px;
  height: 90px;
  background-color: ${({ theme }) => theme.colors.background};
  border-radius: 12px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  img { width: 100%; height: 100%; object-fit: cover; }
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
  text-decoration: none;
  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

const ItemSku = styled.div`
  font-size: 0.8rem;
  color: ${({ theme }) => theme.colors.textMuted};
  margin-bottom: 0.8rem;
`;

const ControlsRow = styled.div`
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
    border: none; width: 32px; height: 32px; cursor: pointer;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
    &:hover:not(:disabled) { background-color: ${({ theme }) => theme.colors.border}; }
    &:disabled { opacity: 0.4; cursor: not-allowed; }
  }

  span { width: 35px; text-align: center; font-weight: bold; color: ${({ theme }) => theme.colors.textMain}; }
`;

const DeleteButton = styled.button`
  color: ${({ theme }) => theme.colors.error};
  background: none; border: none; cursor: pointer; font-size: 0.85rem;
  &:hover { text-decoration: underline; }
`;

const PriceInfo = styled.div`
  text-align: left;
  white-space: nowrap;

  .total { font-weight: bold; font-size: 1.15rem; color: ${({ theme }) => theme.colors.textMain}; }
  .unit { font-size: 0.8rem; color: ${({ theme }) => theme.colors.textMuted}; margin-top: 0.2rem; }
`;

// --- Side Summary Box ---
const SidebarCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  position: sticky; top: 100px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
`;

const DataRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: ${({ theme, bold }) => bold ? theme.colors.textMain : theme.colors.textMuted};
  font-weight: ${({ bold }) => bold ? 'bold' : 'normal'};
  font-size: ${({ bold }) => bold ? '1.15rem' : '0.95rem'};
`;

const BudgetAlert = styled.div`
  background-color: ${({ theme, isOver }) => isOver ? `${theme.colors.error}15` : `${theme.colors.success}15`};
  color: ${({ theme, isOver }) => isOver ? theme.colors.error : theme.colors.success};
  border: 1px solid ${({ theme, isOver }) => isOver ? `${theme.colors.error}30` : `${theme.colors.success}30`};
  padding: 0.8rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-top: 1rem; line-height: 1.5;
`;

const ActionButton = styled.button`
  width: 100%; background-color: ${({ theme }) => theme.colors.primary}; color: #fff;
  border: none; padding: 1rem; border-radius: 10px; font-weight: bold; font-size: 1.05rem;
  cursor: pointer; margin-top: 1.5rem; transition: background-color 0.2s;
  &:hover:not(:disabled) { background-color: ${({ theme }) => theme.colors.secondary}; }
  &:disabled { background-color: ${({ theme }) => theme.colors.border}; cursor: not-allowed; }
`;


export default function WishlistDetailClient({ wishlistId }) {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [wishlist, setWishlist] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price) + ' تومان';

  // دریافت اطلاعات کامل پیش‌فاکتور
  const fetchWishlistDetail = async () => {
    try {
      const res = await apiFetch(`/api/v1/basket/wishlists/${wishlistId}/`);
      if (res.ok) {
        const data = await res.json();
        setWishlist(data);
      } else {
        showToast('پیش‌فاکتور مورد نظر یافت نشد.', 'error');
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (wishlistId) fetchWishlistDetail();
  }, [wishlistId]);

  // تغییر تعداد آیتم درون پیش‌فاکتور
  const handleUpdateQuantity = async (itemId, currentQty, change, maxAvailable) => {
    const newQty = currentQty + change;
    if (newQty < 1) return;
    if (newQty > maxAvailable) return showToast(`موجودی کالا حداکثر ${maxAvailable} عدد است.`, 'warning');

    setActionLoading(itemId);
    try {
      const res = await apiFetch(`/api/v1/basket/wishlists/${wishlistId}/update-item/${itemId}/`, {
        method: 'POST',
        body: JSON.stringify({ quantity: newQty })
      });

      if (!res.ok) throw new Error();
      await fetchWishlistDetail();
    } catch (error) {
      showToast('خطا در تغییر تعداد اقلام.', 'error');
    } finally {
      setActionLoading(null);
    }
  };

  // حذف آیتم از پیش‌فاکتور
  const handleRemoveItem = async (itemId) => {
    setActionLoading(itemId);
    try {
      const res = await apiFetch(`/api/v1/basket/wishlists/${wishlistId}/remove-item/${itemId}/`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error();
      showToast('کالا از لیست حذف شد.', 'success');
      await fetchWishlistDetail();
    } catch (error) {
      showToast('خطا در حذف کالا.', 'error');
      setActionLoading(null);
    }
  };

  // تبدیل پیش‌فاکتور جاری به سبد خرید فعال
  const handleConvert = async () => {
    setActionLoading('convert');
    try {
      const res = await apiFetch(`/api/v1/basket/wishlists/${wishlistId}/convert_to_cart/`, {
        method: 'POST'
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'خطا در تبدیل پیش‌فاکتور.');

      showToast('با موفقیت به سبد خرید فعال تبدیل شد.', 'success');
      setTimeout(() => window.location.href = '/basket/cart', 1200);
    } catch (error) {
      showToast(error.message, 'error');
      setActionLoading(null);
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', width: '100%' }}>در حال بارگذاری جزئیات پیش‌فاکتور...</h2></PageWrapper>;
  if (!wishlist) return <PageWrapper><h2>پیش‌فاکتور یافت نشد.</h2></PageWrapper>;

  // استخراج اقلام سبد متصل به لیست آرزوها
  const items = wishlist.cart?.items || [];

  return (
    <PageWrapper>
      {/* بخش اصلی سمت راست */}
      <div>
        <BackLink href="/basket/wishlists">➡️ بازگشت به لیست پیش‌فاکتورها</BackLink>

        <InfoCard>
          <WishlistTitle>📋 {wishlist.name}</WishlistTitle>
          <Description>{wishlist.description || 'توضیحاتی برای این لیست ثبت نشده است.'}</Description>
          {wishlist.target_date && (
            <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--textMuted)' }}>
              📅 تاریخ برنامه‌ریزی خرید: {new Date(wishlist.target_date).toLocaleDateString('fa-IR')}
            </div>
          )}
        </InfoCard>

        <h2 style={{ fontSize: '1.3rem', marginBottom: '1rem', color: 'var(--textMain)' }}>اقلام ثبت شده</h2>
        <ItemsList>
          {items.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--textMuted)', margin: 0 }}>هیچ کالایی در این لیست وجود ندارد.</p>
          ) : (
            items.map(item => (
              <ItemRow key={item.id}>
                <ItemImage>
                  {item.product_image ? <img src={item.product_image} alt={item.product_name} /> : '📷'}
                </ItemImage>

                <ItemDetails>
                  <ItemTitle href={`/market/product/${item.product}`}>{item.product_name}</ItemTitle>
                  <ItemSku>کد کالا (SKU): {item.product_sku}</ItemSku>

                  <ControlsRow>
                    <QuantitySelector>
                      <button
                        onClick={() => handleUpdateQuantity(item.id, item.quantity, 1, item.market_available)}
                        disabled={actionLoading !== null || item.quantity >= item.market_available}
                      >+</button>
                      <span>{actionLoading === item.id ? '...' : item.quantity}</span>
                      <button
                        onClick={() => handleUpdateQuantity(item.id, item.quantity, -1, item.market_available)}
                        disabled={actionLoading !== null || item.quantity <= 1}
                      >-</button>
                    </QuantitySelector>

                    <DeleteButton onClick={() => handleRemoveItem(item.id)} disabled={actionLoading !== null}>
                      حذف از لیست
                    </DeleteButton>
                  </ControlsRow>
                </ItemDetails>

                <PriceInfo>
                  <div className="total">{formatPrice(item.total_price)}</div>
                  <div className="unit">فی: {formatPrice(item.unit_price)}</div>
                </PriceInfo>
              </ItemRow>
            ))
          )}
        </ItemsList>
      </div>

      {/* بخش خلاصه وضعیت مالی سمت چپ */}
      <div>
        <SidebarCard>
          <h3 style={{ marginBottom: '1.5rem', color: 'var(--textMain)' }}>خلاصه وضعیت مالی</h3>

          <DataRow>
            <span>تعداد کل اقلام:</span>
            <strong>{wishlist.total_quantity} عدد</strong>
          </DataRow>

          <DataRow>
            <span>جمع مبالغ کالاها:</span>
            <strong>{formatPrice(wishlist.subtotal)}</strong>
          </DataRow>

          {wishlist.discount_info?.has_discount && (
            <DataRow style={{ color: 'var(--success)' }}>
              <span>تخفیف تخصیص یافته:</span>
              <strong>- {formatPrice(wishlist.subtotal - wishlist.estimated_total)}</strong>
            </DataRow>
          )}

          <div style={{ height: '1px', backgroundColor: 'var(--border)', margin: '1rem 0' }} />

          <DataRow bold>
            <span>برآورد نهایی:</span>
            <span style={{ color: 'var(--primary)' }}>{formatPrice(wishlist.estimated_total)}</span>
          </DataRow>

          {/* تحلیل هوشمند بودجه بر اساس فیلدهای دیتابیس شما */}
          {wishlist.budget_limit && (
            <BudgetAlert isOver={wishlist.is_over_budget}>
              📌 <strong>سقف بودجه شما:</strong> {formatPrice(wishlist.budget_limit)} <br />
              {wishlist.is_over_budget ? (
                <span>⚠️ هشدار: مبلغ مجموع کالاها از سقف بودجه تعیین‌شده فراتر رفته است!</span>
              ) : (
                <span>✅ موجودی باقی‌مانده از بودجه: {formatPrice(wishlist.budget_remaining)}</span>
              )}
            </BudgetAlert>
          )}

          <ActionButton
            onClick={handleConvert}
            disabled={actionLoading !== null || items.length === 0 || !wishlist.can_convert}
          >
            {actionLoading === 'convert' ? 'در حال تایید...' : '🛒 تایید فاکتور و انتقال به سبد خرید'}
          </ActionButton>
        </SidebarCard>
      </div>
    </PageWrapper>
  );
}