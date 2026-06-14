// src/components/accounts/InvoicesClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1000px;
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
  font-size: 1.6rem;
  color: ${({ theme }) => theme.colors.textMain};
  display: flex;
  align-items: center;
  gap: 0.8rem;
`;

const FilterTabs = styled.div`
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;

  &::-webkit-scrollbar { height: 4px; }
`;

const Tab = styled.button`
  background-color: ${({ theme, $active }) => $active ? theme.colors.primary : theme.colors.surface};
  color: ${({ theme, $active }) => $active ? '#fff' : theme.colors.textMain};
  border: 1px solid ${({ theme, $active }) => $active ? theme.colors.primary : theme.colors.border};
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;

  &:hover {
    background-color: ${({ theme, $active }) => $active ? theme.colors.primary : theme.colors.background};
  }
`;

const InvoicesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const InvoiceCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  }

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const InfoGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
`;

const InvoiceNumber = styled.span`
  font-weight: bold;
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMain};
  font-family: monospace;
`;

const InvoiceDate = styled.span`
  font-size: 0.85rem;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const StatusBadge = styled.span`
  font-size: 0.8rem;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  font-weight: bold;
  background-color: ${({ theme, statusColor }) => `${theme.colors[statusColor]}15` || `${theme.colors.border}50`};
  color: ${({ theme, statusColor }) => theme.colors[statusColor] || theme.colors.textMain};
`;

const PriceArea = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.8rem;

  @media (max-width: 768px) {
    align-items: flex-start;
    width: 100%;
    border-top: 1px solid ${({ theme }) => theme.colors.border};
    padding-top: 1rem;
  }
`;

const PriceText = styled.div`
  font-size: 1.2rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
`;

const ViewButton = styled(Link)`
  background-color: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.textMain};
  border: 1px solid ${({ theme }) => theme.colors.border};
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.2s;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.primary};
  }
`;

// دیکشنری ترجمه وضعیت‌ها و رنگ‌ها
const statusDict = {
  draft: { label: 'پیش‌نویس', color: 'textMuted' },
  pending: { label: 'در انتظار پرداخت', color: 'warning' },
  paid: { label: 'پرداخت شده', color: 'success' },
  partially_paid: { label: 'پرداخت ناقص', color: 'warning' },
  cancelled: { label: 'لغو شده', color: 'error' },
  overdue: { label: 'معوقه', color: 'error' },
};

const typeDict = {
  proforma: 'پیش‌فاکتور',
  final: 'فاکتور فروش',
  wallet_charge: 'شارژ کیف پول',
  refund: 'فاکتور برگشتی',
};

export default function InvoicesClient() {
  const { showToast } = useToast();
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price) + ' تومان';

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const res = await apiFetch('/api/v1/financial/invoices/my_invoices/');
        if (res.ok) {
          const data = await res.json();
          // پشتیبانی از ساختار Pagination جنگو
          setInvoices(data.results || data);
        } else {
          throw new Error('خطا در دریافت فاکتورها');
        }
      } catch (error) {
        showToast('مشکلی در دریافت تاریخچه سفارشات به وجود آمد.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchInvoices();
  }, [showToast]);

  // فیلتر کردن فاکتورها بر اساس تب انتخاب شده
  const filteredInvoices = invoices.filter(invoice => {
    if (activeTab === 'all') return true;
    if (activeTab === 'paid') return invoice.status === 'paid';
    if (activeTab === 'pending') return invoice.status === 'pending' || invoice.status === 'partially_paid';
    if (activeTab === 'cancelled') return invoice.status === 'cancelled';
    return true;
  });

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', padding: '4rem' }}>در حال بارگذاری فاکتورها...</h2></PageWrapper>;

  return (
    <PageWrapper>
      <Header>
        <Title>🧾 تاریخچه سفارشات و فاکتورهای من</Title>
      </Header>

      <FilterTabs style={{ marginBottom: '2rem' }}>
        <Tab $active={activeTab === 'all'} onClick={() => setActiveTab('all')}>همه فاکتورها</Tab>
        <Tab $active={activeTab === 'paid'} onClick={() => setActiveTab('paid')}>پرداخت شده</Tab>
        <Tab $active={activeTab === 'pending'} onClick={() => setActiveTab('pending')}>در انتظار پرداخت</Tab>
        <Tab $active={activeTab === 'cancelled'} onClick={() => setActiveTab('cancelled')}>لغو شده</Tab>
      </FilterTabs>

      {filteredInvoices.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--textMuted)' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📄</div>
          <h3>هیچ فاکتوری در این بخش یافت نشد.</h3>
        </div>
      ) : (
        <InvoicesList>
          {filteredInvoices.map((invoice) => {
            const statusInfo = statusDict[invoice.status] || { label: invoice.status, color: 'textMuted' };
            const typeLabel = typeDict[invoice.invoice_type] || invoice.invoice_type;

            return (
              <InvoiceCard key={invoice.id}>
                <InfoGroup>
                  <InvoiceNumber>{invoice.invoice_number}</InvoiceNumber>
                  <InvoiceDate>
                    ثبت شده در: {new Date(invoice.created_at).toLocaleDateString('fa-IR')}
                  </InvoiceDate>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <StatusBadge statusColor={statusInfo.color}>{statusInfo.label}</StatusBadge>
                    <StatusBadge statusColor="primary">{typeLabel}</StatusBadge>
                  </div>
                </InfoGroup>

                <PriceArea>
                  <PriceText>{formatPrice(invoice.total_amount)}</PriceText>
                  {/* لینک به صفحه جزئیات فاکتور */}
                  <ViewButton href={`/accounts/invoices/${invoice.id}`}>مشاهده جزئیات</ViewButton>
                </PriceArea>
              </InvoiceCard>
            );
          })}
        </InvoicesList>
      )}
    </PageWrapper>
  );
}