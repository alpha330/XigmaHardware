// src/components/accounts/InvoiceDetailClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1100px;
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
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
  text-decoration: none;
  font-weight: bold;
  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

const Card = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
`;

const HeaderRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  padding-bottom: 1rem;

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const Title = styled.h1`
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.textMain};
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Badge = styled.span`
  padding: 0.4rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: bold;
  background-color: ${({ theme, color }) => `${theme.colors[color]}15` || `${theme.colors.border}50`};
  color: ${({ theme, color }) => theme.colors[color] || theme.colors.textMain};
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const InfoBox = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.3rem;

  .label { color: ${({ theme }) => theme.colors.textMuted}; font-size: 0.85rem; }
  .value { color: ${({ theme }) => theme.colors.textMain}; font-weight: bold; font-size: 0.95rem; line-height: 1.5; }
`;

// --- Table Styles ---
const TableWrapper = styled.div`
  overflow-x: auto;
  margin-top: 1rem;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;

  th {
    text-align: right; padding: 1rem;
    background-color: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.textMuted};
    font-size: 0.9rem; border-bottom: 2px solid ${({ theme }) => theme.colors.border};
  }

  td {
    padding: 1rem; border-bottom: 1px solid ${({ theme }) => theme.colors.border};
    color: ${({ theme }) => theme.colors.textMain}; font-size: 0.95rem;
  }
`;

// --- Payment Styles ---
const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  color: ${({ theme, highlight }) => highlight ? theme.colors.textMain : theme.colors.textMuted};
  font-weight: ${({ highlight }) => highlight ? 'bold' : 'normal'};
  font-size: ${({ highlight }) => highlight ? '1.1rem' : '0.95rem'};
`;

const SelectGateway = styled.select`
  width: 100%; background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain}; padding: 1rem;
  border-radius: 8px; margin-top: 1rem; margin-bottom: 1rem; outline: none;
`;

const PayButton = styled.button`
  width: 100%; background-color: ${({ theme }) => theme.colors.success}; color: #fff;
  border: none; padding: 1rem; border-radius: 8px; font-weight: bold; font-size: 1rem;
  cursor: pointer; transition: opacity 0.2s;
  &:hover:not(:disabled) { opacity: 0.9; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

// --- Tracking Styles (New) ---
const TrackingTimeline = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
`;

const TrackingItem = styled.div`
  display: flex;
  gap: 1rem;
  position: relative;

  /* خط عمودی تایم‌لاین */
  &:not(:last-child)::before {
    content: '';
    position: absolute;
    top: 30px;
    right: 11px; /* هماهنگ با سایز دایره */
    width: 2px;
    height: calc(100% - 10px);
    background-color: ${({ theme, active }) => active ? theme.colors.success : theme.colors.border};
  }
`;

const Dot = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: ${({ theme, active }) => active ? theme.colors.success : theme.colors.background};
  border: 3px solid ${({ theme, active }) => active ? theme.colors.success : theme.colors.border};
  display: flex; align-items: center; justify-content: center;
  z-index: 1;
`;

const TrackContent = styled.div`
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  padding: 1rem;
  border-radius: 8px;

  h4 { margin: 0 0 0.4rem 0; color: ${({ theme }) => theme.colors.textMain}; font-size: 1rem; }
  p { margin: 0; color: ${({ theme }) => theme.colors.textMuted}; font-size: 0.85rem; }
`;

// دیکشنری وضعیت‌ها
const statusDict = {
  draft: { label: 'پیش‌نویس', color: 'textMuted' },
  pending: { label: 'در انتظار پرداخت', color: 'warning' },
  paid: { label: 'پرداخت شده', color: 'success' },
  partially_paid: { label: 'پرداخت ناقص', color: 'warning' },
  cancelled: { label: 'لغو شده', color: 'error' },
  overdue: { label: 'معوقه', color: 'error' },
};

// دیکشنری وضعیت‌های لجستیک (Shipment)
const shipmentStatusDict = {
  pending: { label: 'در انتظار تایید انبار', icon: '📦', active: true },
  assigned: { label: 'تخصیص به پیک / پست', icon: '🛵', active: true },
  picked_up: { label: 'دریافت شده توسط پیک', icon: '🚚', active: true },
  delivered: { label: 'تحویل داده شده', icon: '✅', active: true },
  cancelled: { label: 'لغو شده', icon: '❌', active: false },
};

export default function InvoiceDetailClient({ invoiceId }) {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [invoice, setInvoice] = useState(null);

  const [gateways, setGateways] = useState([]);
  const [selectedGateway, setSelectedGateway] = useState('');
  const [payLoading, setPayLoading] = useState(false);

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price) + ' تومان';

  useEffect(() => {
    const fetchInvoiceData = async () => {
      try {
        const res = await apiFetch(`/api/v1/financial/invoices/${invoiceId}/`);
        if (res.ok) {
          const data = await res.json();
          setInvoice(data);

          if (data.status === 'pending' || data.status === 'partially_paid') {
            const gwRes = await apiFetch('/api/v1/payment/active_gateways/');
            if (gwRes.ok) {
              const gwData = await gwRes.json();
              const allGateways = [
                { id: 'wallet', name: 'کیف پول داخلی' },
                ...gwData
              ];
              setGateways(allGateways);
              setSelectedGateway(allGateways[0]?.id);
            }
          }
        } else {
          showToast('سفارش یافت نشد.', 'error');
        }
      } catch (error) {
        showToast('خطا در دریافت اطلاعات فاکتور.', 'error');
      } finally {
        setLoading(false);
      }
    };

    if (invoiceId) fetchInvoiceData();
  }, [invoiceId, showToast]);

  const handlePay = async () => {
    if (!selectedGateway) return showToast('یک روش پرداخت انتخاب کنید.', 'error');
    setPayLoading(true);

    try {
      if (selectedGateway === 'wallet') {
        const payRes = await apiFetch('/api/v1/payment/pay_with_wallet/', {
          method: 'POST',
          body: JSON.stringify({ amount: invoice.remaining_amount, invoice_id: invoice.id })
        });
        const payData = await payRes.json();
        if (!payRes.ok) throw new Error(payData.error || 'موجودی کیف پول کافی نیست.');

        showToast('پرداخت با موفقیت انجام شد!', 'success');
        window.location.reload();
      } else {
        const payRes = await apiFetch('/api/v1/payment/pay/', {
          method: 'POST',
          body: JSON.stringify({
            amount: invoice.remaining_amount,
            invoice_id: invoice.id,
            gateway_id: selectedGateway,
            callback_url: `${window.location.origin}/payment/verify`
          })
        });
        const payData = await payRes.json();
        if (!payRes.ok) throw new Error(payData.error || 'خطا در اتصال به درگاه.');

        window.location.href = payData.payment_url;
      }
    } catch (error) {
      showToast(error.message, 'error');
      setPayLoading(false);
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', width: '100%' }}>در حال دریافت اطلاعات سفارش...</h2></PageWrapper>;
  if (!invoice) return <PageWrapper><h2>سفارشی یافت نشد.</h2></PageWrapper>;

  const statusInfo = statusDict[invoice.status] || { label: invoice.status, color: 'textMuted' };

  // استخراج اطلاعات ارسال (اگر وجود داشته باشد)
  // در بک‌اند شما relation با نام shipments وجود دارد (احتمالاً آرایه است)
  const shipment = invoice.shipments && invoice.shipments.length > 0 ? invoice.shipments[0] : null;

  return (
    <PageWrapper>
      <div>
        <BackLink href="/accounts/invoices">➡️ بازگشت به لیست سفارشات</BackLink>

        <Card>
          <HeaderRow>
            <Title>🧾 سفارش #{invoice.invoice_number}</Title>
            <Badge color={statusInfo.color}>{statusInfo.label}</Badge>
          </HeaderRow>

          <InfoGrid>
            <InfoBox>
              <span className="label">تاریخ ثبت:</span>
              <span className="value">{new Date(invoice.created_at).toLocaleDateString('fa-IR')}</span>
            </InfoBox>
            <InfoBox>
              <span className="label">تحویل گیرنده:</span>
              <span className="value">{invoice.billing_name || 'ثبت نشده'}</span>
            </InfoBox>
            <InfoBox>
              <span className="label">شماره تماس:</span>
              <span className="value" dir="ltr" style={{ textAlign: 'right' }}>{invoice.billing_phone || 'ثبت نشده'}</span>
            </InfoBox>
            <InfoBox style={{ gridColumn: '1 / -1' }}>
              <span className="label">آدرس ارسال:</span>
              <span className="value">{invoice.billing_address || 'آدرس پستی ثبت نشده است.'}</span>
            </InfoBox>
          </InfoGrid>
        </Card>

        {/* 🎯 بخش جدید: پیگیری مرسوله (فقط اگر Shipment وجود داشته باشد) */}
        {shipment && (
          <Card>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: 'var(--textMain)' }}>
              🚚 پیگیری مرسوله
            </h2>

            <div style={{ marginBottom: '1.5rem', backgroundColor: 'var(--background)', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                <InfoBox>
                  <span className="label">کد رهگیری پستی / پیک:</span>
                  <span className="value" dir="ltr">{shipment.courier_tracking_code || 'هنوز صادر نشده'}</span>
                </InfoBox>
                {shipment.courier_name && (
                  <InfoBox>
                    <span className="label">شرکت ارسال‌کننده:</span>
                    <span className="value">{shipment.courier_name}</span>
                  </InfoBox>
                )}
              </div>
            </div>

            <TrackingTimeline>
              {/* اگر بک‌اند شما event های ترکینگ رو می‌فرسته (tracking_events)، روی اون مپ می‌زنیم،
                  در غیر این صورت از وضعیت کلی خود shipment استفاده می‌کنیم. */}
              {shipment.tracking_events && shipment.tracking_events.length > 0 ? (
                shipment.tracking_events.map((event, i) => {
                  const sInfo = shipmentStatusDict[event.status.toLowerCase()] || { label: event.status, icon: '📍', active: true };
                  return (
                    <TrackingItem key={i} active={sInfo.active}>
                      <Dot active={sInfo.active}>{sInfo.icon}</Dot>
                      <TrackContent>
                        <h4>{sInfo.label}</h4>
                        <p>{event.description || 'بدون توضیحات'}</p>
                        <p style={{ marginTop: '0.4rem', color: 'var(--textMuted)', fontSize: '0.8rem' }}>
                          {new Date(event.created_at).toLocaleDateString('fa-IR')} - {new Date(event.created_at).toLocaleTimeString('fa-IR')}
                        </p>
                      </TrackContent>
                    </TrackingItem>
                  );
                })
              ) : (
                <TrackingItem active={true}>
                  <Dot active={true}>📍</Dot>
                  <TrackContent>
                    <h4>{shipmentStatusDict[shipment.status.toLowerCase()]?.label || shipment.status}</h4>
                    <p>در حال بروزرسانی اطلاعات پیک...</p>
                  </TrackContent>
                </TrackingItem>
              )}
            </TrackingTimeline>
          </Card>
        )}

        <Card>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: 'var(--textMain)' }}>اقلام سفارش</h2>
          <TableWrapper>
            <Table>
              <thead>
                <tr>
                  <th>ردیف</th>
                  <th>شرح کالا</th>
                  <th>تعداد</th>
                  <th>قیمت واحد</th>
                  <th>مبلغ کل</th>
                </tr>
              </thead>
              <tbody>
                {invoice.items && invoice.items.length > 0 ? (
                  invoice.items.map((item, index) => (
                    <tr key={item.id}>
                      <td>{index + 1}</td>
                      <td style={{ fontWeight: 'bold' }}>{item.description}</td>
                      <td>{item.quantity}</td>
                      <td>{formatPrice(item.unit_price)}</td>
                      <td style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formatPrice(item.total_price)}</td>
                    </tr>
                  ))
                ) : (
                  <tr><td colSpan="5" style={{ textAlign: 'center' }}>هیچ آیتمی یافت نشد.</td></tr>
                )}
              </tbody>
            </Table>
          </TableWrapper>
        </Card>
      </div>

      <div>
        <Card style={{ position: 'sticky', top: '100px' }}>
          <h3 style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>خلاصه مالی</h3>

          <SummaryRow>
            <span>جمع اقلام:</span>
            <span>{formatPrice(invoice.total_amount - invoice.shipping_amount - invoice.tax_amount + invoice.discount_amount)}</span>
          </SummaryRow>

          {invoice.discount_amount > 0 && (
            <SummaryRow style={{ color: 'var(--success)' }}>
              <span>تخفیف:</span>
              <span>- {formatPrice(invoice.discount_amount)}</span>
            </SummaryRow>
          )}

          {invoice.tax_amount > 0 && (
            <SummaryRow>
              <span>مالیات بر ارزش افزوده:</span>
              <span>{formatPrice(invoice.tax_amount)}</span>
            </SummaryRow>
          )}

          {invoice.shipping_amount > 0 && (
            <SummaryRow>
              <span>هزینه ارسال:</span>
              <span>{formatPrice(invoice.shipping_amount)}</span>
            </SummaryRow>
          )}

          <div style={{ height: '1px', backgroundColor: 'var(--border)', margin: '1rem 0' }} />

          <SummaryRow highlight>
            <span>مبلغ نهایی:</span>
            <span style={{ color: 'var(--primary)' }}>{formatPrice(invoice.total_amount)}</span>
          </SummaryRow>

          <SummaryRow>
            <span>پرداخت شده:</span>
            <span style={{ color: 'var(--success)' }}>{formatPrice(invoice.paid_amount)}</span>
          </SummaryRow>

          {(invoice.status === 'pending' || invoice.status === 'partially_paid') && invoice.remaining_amount > 0 && (
            <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: 'var(--background)', borderRadius: '12px', border: '1px solid var(--warning)' }}>
              <SummaryRow highlight style={{ color: 'var(--error)' }}>
                <span>مبلغ قابل پرداخت:</span>
                <span>{formatPrice(invoice.remaining_amount)}</span>
              </SummaryRow>

              <SelectGateway value={selectedGateway} onChange={(e) => setSelectedGateway(e.target.value)}>
                {gateways.map(gw => (
                  <option key={gw.id} value={gw.id}>{gw.name}</option>
                ))}
              </SelectGateway>

              <PayButton onClick={handlePay} disabled={payLoading || !selectedGateway}>
                {payLoading ? 'انتقال به درگاه...' : 'پرداخت هم‌اکنون'}
              </PayButton>
            </div>
          )}
        </Card>
      </div>
    </PageWrapper>
  );
}