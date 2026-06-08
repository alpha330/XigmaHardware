'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import { useToast } from '@/components/ui/Toast';
import { convertWishlistToCart, deleteWishlist } from '@/lib/api';
import { faShoppingCart, faTrash, faExchangeAlt, faHeart, faCalendar } from '@fortawesome/free-solid-svg-icons';

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const WishlistCard = styled.div`
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  padding: 24px;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;

  &:hover {
    box-shadow: ${p => p.theme.shadows.md};
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const Title = styled.h3`
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 4px;
`;

const Description = styled.p`
  color: ${p => p.theme.colors.text.muted};
  font-size: 0.85rem;
  margin-bottom: 16px;
  flex: 1;
`;

const Stats = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  font-size: 0.85rem;
  color: ${p => p.theme.colors.text.secondary};
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const Price = styled.div`
  font-size: 1.2rem;
  font-weight: 700;
  color: ${p => p.theme.colors.text.primary};
  margin-bottom: 16px;
`;

const Actions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: auto;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 0;
  color: ${p => p.theme.colors.text.muted};
`;

export const WishlistGrid = ({ wishlists }) => {
  const toast = useToast();

  const handleConvert = async (id) => {
    const res = await convertWishlistToCart(id);
    if (res.success) {
      toast.success('به سبد خرید تبدیل شد! 🛒');
      // eslint-disable-next-line react-hooks/immutability
      window.location.href = '/cart';
    } else {
      toast.error(res.error);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('آیا مطمئن هستید؟')) return;
    const res = await deleteWishlist(id);
    if (res.success) {
      toast.success('حذف شد');
      window.location.reload();
    } else {
      toast.error(res.error);
    }
  };

  if (wishlists.length === 0) {
    return (
      <EmptyState>
        <Icon icon={faHeart} size="2xl" />
        <h2 style={{ margin: '16px 0' }}>هیچ علاقه‌مندی ندارید</h2>
        <Button onClick={() => window.location.href = '/products'}>مشاهده محصولات</Button>
      </EmptyState>
    );
  }

  return (
    <Grid>
      {wishlists.map(w => (
        <WishlistCard key={w.id}>
          <CardHeader>
            <div>
              <Title>{w.name || 'سبد آرزو'}</Title>
              {w.target_date && (
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                  <Icon icon={faCalendar} size="xs" /> {w.target_date}
                </div>
              )}
            </div>
          </CardHeader>
          <Description>{w.description || 'بدون توضیح'}</Description>
          <Stats>
            <StatItem>📦 {w.total_items || 0} کالا</StatItem>
            <StatItem>💰 {(w.estimated_total || 0).toLocaleString()} تومان</StatItem>
          </Stats>
          <Price>
            {(w.estimated_total || 0).toLocaleString()} تومان
            {w.discount_percent > 0 && (
              <span style={{ color: '#ef4444', fontSize: '0.9rem', marginRight: 8 }}>
                (-{w.discount_percent}%)
              </span>
            )}
          </Price>
          <Actions>
            <Button variant="primary" icon={faShoppingCart} onClick={() => handleConvert(w.id)} fullWidth>
              تبدیل به سبد خرید
            </Button>
            <Button variant="danger" icon={faTrash} onClick={() => handleDelete(w.id)} />
          </Actions>
        </WishlistCard>
      ))}
    </Grid>
  );
};