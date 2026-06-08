'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import { useToast } from '@/components/ui/Toast';
import { createPayment, payWithWallet, createInvoiceFromCart } from '@/lib/api';
import { faWallet, faCreditCard, faCheck, faTruck, faLocationDot } from '@fortawesome/free-solid-svg-icons';

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 32px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
`;

const Section = styled.div`
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  padding: 24px;
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  font-weight: 700;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AddressCard = styled.div`
  padding: 16px;
  border: 2px solid ${p => p.$selected ? p.theme.colors.brand[500] : p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.md};
  cursor: pointer;
  transition: all 0.15s;
  background: ${p => p.$selected ? p.theme.colors.brand[50] : 'transparent'};

  &:hover { border-color: ${p => p.theme.colors.brand[300]}; }
`;

const PaymentMethod = styled.div`
  padding: 16px;
  border: 2px solid ${p => p.$selected ? p.theme.colors.brand[500] : p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.md};
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;

  &:hover { border-color: ${p => p.theme.colors.brand[300]}; }
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  &.total { font-weight: 700; font-size: 1.15rem; border-top: 1px solid ${p => p.theme.colors.border.light}; padding-top: 16px; margin-top: 16px; }
`;

export const CheckoutClient = ({ initialAddresses, initialWallet, initialCart }) => {
  const [selectedAddress, setSelectedAddress] = useState(initialAddresses?.[0]?.id || null);
  const [paymentMethod, setPaymentMethod] = useState('wallet');
  const [loading, setLoading] = useState(false);
  const toast = useToast();
  const router = useRouter();

  const addresses = Array.isArray(initialAddresses) ? initialAddresses : initialAddresses?.results || [];
  const wallet = initialWallet?.wallet || initialWallet;
  const cart = initialCart;

  const handlePay = async () => {
    if (!selectedAddress) { toast.warning('لطفاً آدرس تحویل را انتخاب کنید'); return; }
    setLoading(true);

    try {
      // ایجاد فاکتور از سبد
      const invoiceRes = await createInvoiceFromCart(paymentMethod);
      if (!invoiceRes.success) { toast.error(invoiceRes.error); setLoading(false); return; }

      // پرداخت
      if (paymentMethod === 'wallet') {
        const payRes = await payWithWallet(invoiceRes.data.total_amount, `پرداخت فاکتور ${invoiceRes.data.invoice_number}`);
        if (payRes.success) {
          toast.success('پرداخت با موفقیت انجام شد! 🎉');
          router.push('/dashboard/orders');
        } else {
          toast.error(payRes.error);
        }
      } else {
        const payRes = await createPayment(invoiceRes.data.total_amount, `پرداخت فاکتور ${invoiceRes.data.invoice_number}`);
        if (payRes.success) {
          window.location.href = payRes.data.payment_url;
        } else {
          toast.error(payRes.error);
        }
      }
    } catch (e) {
      toast.error('خطا در پرداخت');
    }
    setLoading(false);
  };

  return (
    <Grid>
      <div>
        {/* آدرس */}
        <Section>
          <SectionTitle><Icon icon={faLocationDot} /> آدرس تحویل</SectionTitle>
          {addresses.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>آدرسی ثبت نشده. <a href="/dashboard/addresses">افزودن آدرس</a></p>
          ) : (
            addresses.map(addr => (
              <AddressCard key={addr.id} $selected={selectedAddress === addr.id} onClick={() => setSelectedAddress(addr.id)} style={{ marginBottom: 12 }}>
                <div style={{ fontWeight: 600 }}>{addr.title} - {addr.recipient_name}</div>
                <div style={{ color: '#64748b', fontSize: '0.9rem' }}>{addr.full_address}</div>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>{addr.recipient_mobile}</div>
              </AddressCard>
            ))
          )}
        </Section>

        {/* روش پرداخت */}
        <Section>
          <SectionTitle><Icon icon={faCreditCard} /> روش پرداخت</SectionTitle>
          <PaymentMethod $selected={paymentMethod === 'wallet'} onClick={() => setPaymentMethod('wallet')}>
            <Icon icon={faWallet} size="lg" />
            <div>
              <div style={{ fontWeight: 600 }}>کیف پول</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>موجودی: {wallet?.balance?.toLocaleString() || 0} تومان</div>
            </div>
            {paymentMethod === 'wallet' && <Icon icon={faCheck} style={{ marginRight: 'auto', color: '#8b5cf6' }} />}
          </PaymentMethod>
          <PaymentMethod $selected={paymentMethod === 'gateway'} onClick={() => setPaymentMethod('gateway')}>
            <Icon icon={faCreditCard} size="lg" />
            <div>
              <div style={{ fontWeight: 600 }}>درگاه پرداخت</div>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>پرداخت از طریق PayPing</div>
            </div>
            {paymentMethod === 'gateway' && <Icon icon={faCheck} style={{ marginRight: 'auto', color: '#8b5cf6' }} />}
          </PaymentMethod>
        </Section>
      </div>

      {/* خلاصه سفارش */}
      <div style={{ position: 'sticky', top: 96, alignSelf: 'start' }}>
        <Section>
          <SectionTitle>خلاصه سفارش</SectionTitle>
          <SummaryRow><span>تعداد کالا</span><span>{cart?.total_quantity || 0}</span></SummaryRow>
          <SummaryRow><span>جمع</span><span>{cart?.subtotal?.toLocaleString() || 0} تومان</span></SummaryRow>
          {cart?.discount_total > 0 && <SummaryRow style={{ color: '#ef4444' }}><span>تخفیف</span><span>-{cart.discount_total?.toLocaleString()} تومان</span></SummaryRow>}
          <SummaryRow className="total"><span>مبلغ نهایی</span><span>{cart?.grand_total?.toLocaleString() || 0} تومان</span></SummaryRow>
          <Button variant="primary" size="lg" fullWidth style={{ marginTop: 20 }} loading={loading} onClick={handlePay}>
            {paymentMethod === 'wallet' ? 'پرداخت با کیف پول' : 'رفتن به درگاه پرداخت'}
          </Button>
        </Section>
      </div>
    </Grid>
  );
};