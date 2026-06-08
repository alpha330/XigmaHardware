'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import { useToast } from '@/components/ui/Toast';
import { setWishlistDiscount, clearDiscount } from '@/lib/api';
import { faPercent, faTrash, faCheck } from '@fortawesome/free-solid-svg-icons';

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  overflow: hidden;
`;

const Th = styled.th`
  text-align: right;
  padding: 14px 16px;
  background: ${p => p.theme.colors.bg.tertiary};
  font-size: 0.85rem;
  color: ${p => p.theme.colors.text.secondary};
  font-weight: 600;
  border-bottom: 1px solid ${p => p.theme.colors.border.light};
`;

const Td = styled.td`
  padding: 14px 16px;
  border-bottom: 1px solid ${p => p.theme.colors.border.light};
  font-size: 0.9rem;
`;

const DiscountInput = styled.input`
  width: 80px;
  padding: 6px 10px;
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.sm};
  text-align: center;
  font-family: inherit;
  font-size: 0.9rem;
`;

export const DiscountsList = ({ wishlists }) => {
  const [discounts, setDiscounts] = useState({});
  const toast = useToast();

  const handleApply = async (wishlistId) => {
    const percent = parseFloat(discounts[wishlistId]);
    if (!percent || percent < 0 || percent > 100) {
      toast.warning('درصد تخفیف باید بین ۰ تا ۱۰۰ باشد');
      return;
    }

    const res = await setWishlistDiscount(wishlistId, percent);
    if (res.success) {
      toast.success(`تخفیف ${percent}% اعمال شد`);
      setDiscounts({ ...discounts, [wishlistId]: '' });
    } else {
      toast.error(res.error);
    }
  };

  const handleClear = async (wishlistId) => {
    const res = await clearDiscount(wishlistId);
    if (res.success) {
      toast.success('تخفیف حذف شد');
    } else {
      toast.error(res.error);
    }
  };

  const wishlistItems = wishlists.filter(w => w.cart_type === 'wishlist' || w.is_wishlist);

  if (wishlistItems.length === 0) {
    return <p style={{ color: '#94a3b8' }}>هیچ سبد آرزویی برای تخفیف وجود ندارد.</p>;
  }

  return (
    <Table>
      <thead>
        <tr>
          <Th>کاربر</Th>
          <Th>نام سبد</Th>
          <Th>تعداد اقلام</Th>
          <Th>مبلغ کل</Th>
          <Th>تخفیف فعلی</Th>
          <Th>تخفیف جدید</Th>
          <Th>عملیات</Th>
        </tr>
      </thead>
      <tbody>
        {wishlistItems.map(w => (
          <tr key={w.id}>
            <Td>{w.user_name || w.user || '-'}</Td>
            <Td>{w.name || 'سبد آرزو'}</Td>
            <Td>{w.total_items || 0}</Td>
            <Td>{(w.subtotal || 0).toLocaleString()} تومان</Td>
            <Td>
              {w.discount_percent > 0 ? (
                <span style={{ color: '#ef4444', fontWeight: 600 }}>-{w.discount_percent}%</span>
              ) : (
                <span style={{ color: '#94a3b8' }}>-</span>
              )}
            </Td>
            <Td>
              <DiscountInput
                type="number"
                min="0"
                max="100"
                placeholder="%"
                value={discounts[w.id] || ''}
                onChange={(e) => setDiscounts({ ...discounts, [w.id]: e.target.value })}
              />
            </Td>
            <Td>
              <div style={{ display: 'flex', gap: 4 }}>
                <Button variant="primary" size="sm" icon={faCheck} onClick={() => handleApply(w.id)}>
                  اعمال
                </Button>
                {w.discount_percent > 0 && (
                  <Button variant="danger" size="sm" icon={faTrash} onClick={() => handleClear(w.id)}>
                    حذف
                  </Button>
                )}
              </div>
            </Td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};