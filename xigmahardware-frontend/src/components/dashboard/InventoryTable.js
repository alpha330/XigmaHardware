'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useToast } from '@/components/ui/Toast';
import { addStock, removeStock, transferStock } from '@/lib/api';
import {
  faSearch, faBoxes, faWarehouse, faPlus, faMinus,
  faExchangeAlt, faCheck, faTimes, faLocationDot,
} from '@fortawesome/free-solid-svg-icons';

// ==================== Styled Components ====================

const FiltersBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
`;

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

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 500;
  background: ${p => p.$bg};
  color: ${p => p.$color};
`;

const QtyCell = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const QtyButton = styled.button`
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid ${p => p.theme.colors.border.light};
  background: ${p => p.theme.colors.bg.tertiary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${p => p.theme.colors.text.primary};
  transition: all 0.15s;

  &:hover {
    background: ${p => p.theme.colors.brand[50]};
    color: ${p => p.theme.colors.brand[600]};
  }
`;

const LocationLink = styled.a`
  color: ${p => p.theme.colors.brand[600]};
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;

  &:hover { text-decoration: underline; }
`;

const LowStockAlert = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: ${p => p.theme.colors.danger};
  font-weight: 600;
  font-size: 0.8rem;
`;

// ==================== Helpers ====================

const statusConfig = {
  in_stock: { icon: faCheck, label: 'موجود', bg: '#ecfdf5', color: '#059669' },
  reserved: { icon: faCheck, label: 'رزرو شده', bg: '#eff6ff', color: '#2563eb' },
  in_transit: { icon: faExchangeAlt, label: 'در راه', bg: '#fffbeb', color: '#d97706' },
  damaged: { icon: faTimes, label: 'آسیب‌دیده', bg: '#fef2f2', color: '#dc2626' },
  returned: { icon: faExchangeAlt, label: 'برگشتی', bg: '#faf5ff', color: '#8b5cf6' },
};

// ==================== Component ====================

export const InventoryTable = ({ items, warehouseFilter, searchQuery }) => {
  const router = useRouter();
  const toast = useToast();
  const [search, setSearch] = useState(searchQuery || '');
  const [quantities, setQuantities] = useState({});

  const handleSearch = (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (warehouseFilter) params.set('warehouse', warehouseFilter);
    if (search) params.set('search', search);
    router.push(`/dashboard/inventory?${params.toString()}`);
  };

  const handleAddStock = async (itemId, qty) => {
    const res = await addStock(itemId, qty);
    if (res.success) {
      toast.success(`${qty} عدد اضافه شد`);
      router.refresh();
    } else {
      toast.error(res.error);
    }
  };

  const handleRemoveStock = async (itemId, qty) => {
    const res = await removeStock(itemId, qty);
    if (res.success) {
      toast.success(`${qty} عدد کم شد`);
      router.refresh();
    } else {
      toast.error(res.error);
    }
  };

  if (items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>
        <Icon icon={faBoxes} size="2xl" />
        <p>هیچ موجودی یافت نشد.</p>
      </div>
    );
  }

  return (
    <>
      <FiltersBar>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8, flex: 1 }}>
          <Input
            placeholder="جستجوی محصول یا SKU..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            icon={faSearch}
            style={{ marginBottom: 0 }}
          />
          <Button variant="primary" type="submit">
            جستجو
          </Button>
        </form>
      </FiltersBar>

      <Table>
        <thead>
          <tr>
            <Th>محصول</Th>
            <Th>SKU</Th>
            <Th>انبار</Th>
            <Th>موجودی</Th>
            <Th>رزرو</Th>
            <Th>وضعیت</Th>
            <Th>موقعیت</Th>
            <Th>عملیات سریع</Th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => {
            const status = statusConfig[item.status] || statusConfig.in_stock;
            return (
              <tr key={item.id}>
                <Td>
                  <div style={{ fontWeight: 600 }}>{item.product_name || item.product}</div>
                </Td>
                <Td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                  {item.product_sku || '-'}
                </Td>
                <Td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Icon icon={faWarehouse} size="xs" />
                    {item.warehouse_name || item.warehouse}
                  </div>
                </Td>
                <Td>
                  <QtyCell>
                    <span style={{ fontWeight: 700 }}>{item.quantity}</span>
                    <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>
                      (قابل برداشت: {item.available_quantity})
                    </span>
                  </QtyCell>
                  {item.is_low_stock && (
                    <LowStockAlert>
                      ⚠️ موجودی کم
                    </LowStockAlert>
                  )}
                </Td>
                <Td>{item.reserved_quantity || 0}</Td>
                <Td>
                  <StatusBadge $bg={status.bg} $color={status.color}>
                    <Icon icon={status.icon} size="xs" />
                    {status.label}
                  </StatusBadge>
                </Td>
                <Td>
                  {item.location && item.location !== '-' ? (
                    <LocationLink href="#" title={item.location}>
                      <Icon icon={faLocationDot} size="xs" />
                      {item.shelf || item.location}
                    </LocationLink>
                  ) : (
                    '-'
                  )}
                </Td>
                <Td>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <QtyButton onClick={() => handleAddStock(item.id, 1)} title="افزایش ۱ عدد">
                      <Icon icon={faPlus} size="xs" />
                    </QtyButton>
                    <QtyButton onClick={() => handleRemoveStock(item.id, 1)} title="کاهش ۱ عدد">
                      <Icon icon={faMinus} size="xs" />
                    </QtyButton>
                  </div>
                </Td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    </>
  );
};