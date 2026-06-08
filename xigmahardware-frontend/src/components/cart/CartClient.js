'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import { useToast } from '@/components/ui/Toast';
import { updateCartItem, removeCartItem, clearCart } from '@/lib/api';
import { faTrash, faPlus, faMinus, faShoppingBag, faArrowLeft } from '@fortawesome/free-solid-svg-icons';

const Container = styled.div`
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 32px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
`;

const ItemsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const CartItem = styled.div`
  display: flex;
  gap: 20px;
  padding: 20px;
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  transition: all 0.2s;

  &:hover { border-color: ${p => p.theme.colors.brand[300]}; }

  @media (max-width: 480px) { flex-direction: column; }
`;

const ItemImage = styled.div`
  width: 100px;
  height: 100px;
  background: ${p => p.theme.colors.bg.tertiary};
  border-radius: ${p => p.theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  flex-shrink: 0;
`;

const ItemInfo = styled.div`
  flex: 1;
`;

const ItemTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 8px;
`;

const ItemPrice = styled.div`
  font-weight: 700;
  color: ${p => p.theme.colors.text.primary};
  margin-top: 8px;
`;

const QuantityControl = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
`;

const QtyButton = styled.button`
  width: 32px;
  height: 32px;
  border-radius: ${p => p.theme.borderRadius.sm};
  border: 1px solid ${p => p.theme.colors.border.light};
  background: ${p => p.theme.colors.bg.tertiary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${p => p.theme.colors.text.primary};
  transition: all 0.15s;

  &:hover { background: ${p => p.theme.colors.brand[50]}; color: ${p => p.theme.colors.brand[600]}; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

const QtyDisplay = styled.span`
  min-width: 32px;
  text-align: center;
  font-weight: 600;
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: ${p => p.theme.colors.text.muted};
  cursor: pointer;
  padding: 8px;
  border-radius: ${p => p.theme.borderRadius.sm};
  transition: all 0.15s;

  &:hover { color: ${p => p.theme.colors.danger}; background: ${p => p.theme.colors.danger}10; }
`;

const Sidebar = styled.div`
  position: sticky;
  top: 96px;
  align-self: start;
`;

const SummaryCard = styled.div`
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  padding: 24px;
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 0.95rem;

  &.total {
    font-weight: 700;
    font-size: 1.15rem;
    border-top: 1px solid ${p => p.theme.colors.border.light};
    padding-top: 16px;
    margin-top: 16px;
  }

  &.discount {
    color: ${p => p.theme.colors.danger};
  }
`;

const EmptyCart = styled.div`
  text-align: center;
  padding: 80px 0;
  color: ${p => p.theme.colors.text.muted};
`;

export const CartClient = ({ initialCart }) => {
  const [cart, setCart] = useState(initialCart);
  const [loading, setLoading] = useState(false);
  const toast = useToast();
  const router = useRouter();

  const items = cart?.items || [];
  const isEmpty = items.length === 0;

  const handleQuantityChange = async (itemId, newQty) => {
    if (newQty < 1) return;
    setLoading(true);
    const res = await updateCartItem(itemId, newQty);
    if (res.success) {
      setCart(prev => ({
        ...prev,
        items: prev.items.map(i => i.id === itemId ? { ...i, quantity: newQty, total_price: i.unit_price * newQty } : i),
        subtotal: prev.items.reduce((sum, i) => sum + (i.id === itemId ? i.unit_price * newQty : i.total_price), 0),
      }));
    } else {
      toast.error(res.error);
    }
    setLoading(false);
  };

  const handleRemove = async (itemId) => {
    setLoading(true);
    const res = await removeCartItem(itemId);
    if (res.success) {
      const newItems = cart.items.filter(i => i.id !== itemId);
      setCart(prev => ({
        ...prev,
        items: newItems,
        subtotal: newItems.reduce((sum, i) => sum + i.total_price, 0),
        total_items: newItems.length,
      }));
      toast.success('آیتم حذف شد');
    } else {
      toast.error(res.error);
    }
    setLoading(false);
  };

  if (isEmpty) {
    return (
      <EmptyCart>
        <Icon icon={faShoppingBag} size="2xl" />
        <h2 style={{ margin: '16px 0' }}>سبد خرید شما خالی است</h2>
        <Button onClick={() => router.push('/products')}>مشاهده محصولات</Button>
      </EmptyCart>
    );
  }

  return (
    <Container>
      <ItemsList>
        {items.map(item => (
          <CartItem key={item.id}>
            <ItemImage>{item.product_image ? <img src={item.product_image} alt="" /> : '📦'}</ItemImage>
            <ItemInfo>
              <ItemTitle>{item.product_name}</ItemTitle>
              <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>SKU: {item.product_sku}</div>
              <QuantityControl>
                <QtyButton onClick={() => handleQuantityChange(item.id, item.quantity - 1)} disabled={loading}><Icon icon={faMinus} size="xs" /></QtyButton>
                <QtyDisplay>{item.quantity}</QtyDisplay>
                <QtyButton onClick={() => handleQuantityChange(item.id, item.quantity + 1)} disabled={loading}><Icon icon={faPlus} size="xs" /></QtyButton>
              </QuantityControl>
              <ItemPrice>{item.total_price?.toLocaleString()} <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>تومان</span></ItemPrice>
            </ItemInfo>
            <RemoveButton onClick={() => handleRemove(item.id)} disabled={loading}><Icon icon={faTrash} size="sm" /></RemoveButton>
          </CartItem>
        ))}
      </ItemsList>

      <Sidebar>
        <SummaryCard>
          <h3 style={{ fontWeight: 700, marginBottom: 20 }}>خلاصه سفارش</h3>
          <SummaryRow><span>تعداد کالا</span><span>{cart.total_quantity}</span></SummaryRow>
          <SummaryRow><span>جمع سبد</span><span>{cart.subtotal?.toLocaleString()} تومان</span></SummaryRow>
          {cart.discount_total > 0 && (
            <SummaryRow className="discount"><span>تخفیف</span><span>-{cart.discount_total?.toLocaleString()} تومان</span></SummaryRow>
          )}
          <SummaryRow className="total"><span>مبلغ نهایی</span><span>{cart.grand_total?.toLocaleString()} تومان</span></SummaryRow>
          <Button variant="primary" size="lg" fullWidth style={{ marginTop: 20 }} onClick={() => router.push('/checkout')}>
            ادامه به پرداخت
          </Button>
        </SummaryCard>
      </Sidebar>
    </Container>
  );
};