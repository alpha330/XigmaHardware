// src/components/basket/WishlistClient.jsx
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
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const Title = styled.h1`
  font-size: 1.8rem;
  color: ${({ theme }) => theme.colors.textMain};
  display: flex;
  align-items: center;
  gap: 0.8rem;
`;

const CreateButton = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;

  &:hover { background-color: ${({ theme }) => theme.colors.secondary}; }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
`;

const WishlistCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
`;

const CardTitle = styled.h3`
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin: 0 0 0.4rem 0;
`;

const Badge = styled.span`
  background-color: ${({ theme, hasDiscount }) => hasDiscount ? `${theme.colors.success}15` : `${theme.colors.primary}15`};
  color: ${({ theme, hasDiscount }) => hasDiscount ? theme.colors.success : theme.colors.primary};
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
`;

const Description = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  flex-grow: 1;
`;

const StatsRow = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  color: ${({ theme }) => theme.colors.textMain};

  strong { color: ${({ theme }) => theme.colors.textMain}; }
`;

const Divider = styled.div`
  height: 1px;
  background-color: ${({ theme }) => theme.colors.border};
  margin: 1rem 0;
`;

const Actions = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: auto;
`;

const ActionBtn = styled.button`
  flex: 1;
  padding: 0.8rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid ${({ theme, variant }) => variant === 'outline' ? theme.colors.border : 'transparent'};
  background-color: ${({ theme, variant }) => variant === 'outline' ? 'transparent' : theme.colors.primary};
  color: ${({ theme, variant }) => variant === 'outline' ? theme.colors.textMain : '#fff'};

  &:hover:not(:disabled) {
    background-color: ${({ theme, variant }) => variant === 'outline' ? theme.colors.background : theme.colors.secondary};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

export default function WishlistClient() {
  const { showToast } = useToast();
  const [wishlists, setWishlists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price) + ' تومان';

  const fetchWishlists = async () => {
    try {
      const res = await apiFetch('/api/v1/basket/wishlists/');
      if (res.ok) {
        const data = await res.json();
        setWishlists(data);
      }
    } catch (error) {
      console.error('Fetch wishlists error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchWishlists();
  }, []);

  // هندلر تبدیل پیش‌فاکتور به سبد خرید نهایی
  const handleConvertToCart = async (wishlistId) => {
    setActionLoading(wishlistId);
    try {
      const res = await apiFetch(`/api/v1/basket/wishlists/${wishlistId}/convert_to_cart/`, {
        method: 'POST'
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'خطا در انتقال به سبد خرید.');

      showToast('پیش‌فاکتور با موفقیت به سبد خرید تبدیل شد.', 'success');
      // هدایت کاربر به سبد خرید پس از ۱.۵ ثانیه
      setTimeout(() => window.location.href = '/basket/cart', 1500);

    } catch (error) {
      showToast(error.message, 'error');
      setActionLoading(null);
    }
  };

  // ایجاد یک لیست جدید (تستی سریع برای رابط کاربری)
  const handleCreateNew = async () => {
    const name = prompt('لطفا یک نام برای پیش‌فاکتور/لیست جدید خود وارد کنید:');
    if (!name) return;

    try {
      const res = await apiFetch('/api/v1/basket/wishlists/', {
        method: 'POST',
        body: JSON.stringify({ name, description: 'ایجاد شده از طریق پنل کاربری' })
      });

      if (!res.ok) throw new Error('خطا در ساخت لیست جدید.');

      showToast('لیست جدید با موفقیت ایجاد شد.', 'success');
      fetchWishlists();
    } catch (error) {
      showToast(error.message, 'error');
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', padding: '4rem' }}>در حال بارگذاری پیش‌فاکتورها...</h2></PageWrapper>;

  return (
    <PageWrapper>
      <Header>
        <Title>⭐ پیش‌فاکتورها و لیست‌های من</Title>
        <CreateButton onClick={handleCreateNew}>
          ➕ ایجاد لیست جدید
        </CreateButton>
      </Header>

      {wishlists.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--textMuted)' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📋</div>
          <h3>شما هنوز هیچ پیش‌فاکتور یا لیستی ایجاد نکرده‌اید.</h3>
          <p>می‌توانید سبدهای خرید خود را برای آینده ذخیره کنید تا مدیریت بهتری روی بودجه داشته باشید.</p>
        </div>
      ) : (
        <Grid>
          {wishlists.map((list) => (
            <WishlistCard key={list.id}>
              <CardHeader>
                <div>
                  <CardTitle>{list.name}</CardTitle>
                  <span style={{ fontSize: '0.8rem', color: 'var(--textMuted)' }}>
                    تاریخ ایجاد: {new Date(list.created_at).toLocaleDateString('fa-IR')}
                  </span>
                </div>
                {list.discount_info?.has_discount && (
                  <Badge hasDiscount>دارای تخفیف ویژه</Badge>
                )}
              </CardHeader>

              <Description>
                {list.description || 'بدون توضیحات اضافی'}
              </Description>

              <StatsRow>
                <span>تعداد اقلام:</span>
                <strong>{list.total_items} کالا ({list.total_quantity} عدد)</strong>
              </StatsRow>

              <StatsRow>
                <span>جمع کل (بدون تخفیف):</span>
                <strong>{formatPrice(list.subtotal)}</strong>
              </StatsRow>

              {list.discount_info?.has_discount && (
                <StatsRow style={{ color: 'var(--success)' }}>
                  <span>تخفیف اعمال شده:</span>
                  <strong>- {formatPrice(list.subtotal - list.estimated_total)}</strong>
                </StatsRow>
              )}

              <Divider />

              <StatsRow style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
                <span>مبلغ نهایی:</span>
                <span style={{ color: 'var(--primary)' }}>{formatPrice(list.estimated_total)}</span>
              </StatsRow>

              <Actions>
                <ActionBtn
                  onClick={() => handleConvertToCart(list.id)}
                  disabled={!list.can_convert || actionLoading === list.id || list.total_items === 0}
                >
                  {actionLoading === list.id ? 'در حال انتقال...' : 'تبدیل به سبد خرید'}
                </ActionBtn>
                {/* دکمه زیر می‌تواند به صفحه‌ای برود که کاربر اقلام داخل این لیست را ببیند و مدیریت کند */}
                <Link href={`/basket/wishlists/${list.id}`} style={{ flex: 1, display: 'block' }}>
                  <ActionBtn variant="outline" style={{ width: '100%' }}>
                    مشاهده اقلام
                  </ActionBtn>
                </Link>
              </Actions>
            </WishlistCard>
          ))}
        </Grid>
      )}
    </PageWrapper>
  );
}