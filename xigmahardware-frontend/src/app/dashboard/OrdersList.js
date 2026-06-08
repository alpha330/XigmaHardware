'use client';

import styled from '@emotion/styled';
import { Icon } from '@/components/ui/Icon';
import { faBox, faClock, faCheckCircle, faTruck, faTimesCircle } from '@fortawesome/free-solid-svg-icons';

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

const statusMap = {
  paid: { icon: faCheckCircle, label: 'پرداخت شده', bg: '#ecfdf5', color: '#059669' },
  pending: { icon: faClock, label: 'در انتظار', bg: '#fffbeb', color: '#d97706' },
  shipped: { icon: faTruck, label: 'ارسال شده', bg: '#eff6ff', color: '#2563eb' },
  cancelled: { icon: faTimesCircle, label: 'لغو شده', bg: '#fef2f2', color: '#dc2626' },
};

export const OrdersList = ({ invoices, error }) => {
  if (error) return <div>خطا در بارگذاری سفارشات</div>;
  if (invoices.length === 0) return <p style={{ color: '#94a3b8' }}>هنوز سفارشی ثبت نشده است.</p>;

  return (
    <Table>
      <thead>
        <tr>
          <Th>شماره فاکتور</Th>
          <Th>تاریخ</Th>
          <Th>مبلغ</Th>
          <Th>وضعیت</Th>
          <Th>جزئیات</Th>
        </tr>
      </thead>
      <tbody>
        {invoices.map(inv => {
          const status = statusMap[inv.status] || statusMap.pending;
          return (
            <tr key={inv.id}>
              <Td style={{ fontFamily: 'monospace' }}>{inv.invoice_number}</Td>
              <Td>{inv.created_at_jalali}</Td>
              <Td>{inv.total_amount?.toLocaleString()} تومان</Td>
              <Td>
                <StatusBadge $bg={status.bg} $color={status.color}>
                  <Icon icon={status.icon} size="xs" /> {status.label}
                </StatusBadge>
              </Td>
              <Td>
                <a href={`/dashboard/orders/${inv.id}`} style={{ color: '#8b5cf6' }}>
                  مشاهده
                </a>
              </Td>
            </tr>
          );
        })}
      </tbody>
    </Table>
  );
};