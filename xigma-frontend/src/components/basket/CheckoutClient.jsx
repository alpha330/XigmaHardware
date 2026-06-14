// src/components/basket/CheckoutClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const SectionTitle = styled.h2`
  font-size: 1.4rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

const Card = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
  margin-bottom: 2rem;
`;

const FormGrid = styled.form`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  grid-column: ${({ fullWidth }) => fullWidth ? '1 / -1' : 'auto'};
`;

const Label = styled.label`
  color: ${({ theme }) => theme.colors.textMain};
  font-size: 0.9rem;
  font-weight: bold;
`;

const Input = styled.input`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-family: inherit;
  outline: none;
  &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
`;

const TextArea = styled.textarea`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-family: inherit;
  outline: none;
  min-height: 80px;
  resize: vertical;
  &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
`;

const GatewayGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const GatewayCard = styled.div`
  border: 2px solid ${({ theme, selected }) => selected ? theme.colors.primary : theme.colors.border};
  background-color: ${({ theme, selected }) => selected ? `${theme.colors.primary}10` : theme.colors.background};
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
  }

  .icon { font-size: 2rem; margin-bottom: 0.5rem; display: block; }
  .name { font-weight: bold; font-size: 0.95rem; color: ${({ theme }) => theme.colors.textMain}; }
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: ${({ theme, highlight }) => highlight ? theme.colors.textMain : theme.colors.textMuted};
  font-weight: ${({ highlight }) => highlight ? 'bold' : 'normal'};
  font-size: ${({ highlight }) => highlight ? '1.2rem' : '1rem'};
`;

const PayButton = styled.button`
  width: 100%;
  background-color: ${({ theme }) => theme.colors.success};
  color: #fff;
  border: none;
  padding: 1.2rem;
  border-radius: 10px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  margin-top: 1.5rem;
  transition: all 0.2s;

  &:hover:not(:disabled) { opacity: 0.9; }
  &:disabled { background-color: ${({ theme }) => theme.colors.border}; cursor: not-allowed; }
`;

export default function CheckoutClient() {
  const { showToast } = useToast();
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [cart, setCart] = useState(null);
  const [gateways, setGateways] = useState([]);
  const [selectedGateway, setSelectedGateway] = useState(null);

  const [billingInfo, setBillingInfo] = useState({
    billing_name: '',
    billing_phone: '',
    billing_postal_code: '',
    billing_address: '',
    customer_notes: ''
  });

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price) + ' تومان';

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [cartRes, profileRes, userRes, gatewaysRes] = await Promise.all([
          apiFetch('/api/v1/basket/carts/my_cart/'),
          apiFetch('/api/v1/accounts/me/profile/'),
          apiFetch('/api/v1/accounts/me/'),
          apiFetch('/api/v1/payment/active_gateways/')
        ]);

        if (cartRes.ok) {
          const cartData = await cartRes.json();
          if (!cartData.can_checkout) {
            showToast('سبد خرید شما برای پرداخت آماده نیست.', 'error');
            return router.push('/basket/cart');
          }
          setCart(cartData);
        } else {
          return router.push('/basket/cart');
        }

        let name = '', phone = '', address = '', postal = '';
        if (userRes.ok) {
          const u = await userRes.json();
          name = `${u.first_name || ''} ${u.last_name || ''}`.trim();
          phone = u.mobile || '';
        }
        if (profileRes.ok) {
          const p = await profileRes.json();
          const profileData = p.profile || p;
          address = profileData.address || '';
          postal = profileData.postal_code || '';
        }

        setBillingInfo({ billing_name: name, billing_phone: phone, billing_address: address, billing_postal_code: postal, customer_notes: '' });

        if (gatewaysRes.ok) {
          const gwData = await gatewaysRes.json();
          const allGateways = [
            { id: 'wallet', name: 'کیف پول داخلی', type: 'wallet', type_display: { icon: '💰' } },
            ...gwData
          ];
          setGateways(allGateways);
          setSelectedGateway(allGateways[0]?.id);
        }

      } catch (error) {
        showToast('خطا در دریافت اطلاعات. لطفا صفحه را رفرش کنید.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [router, showToast]);

  const handleCheckout = async (e) => {
    e.preventDefault();
    if (!selectedGateway) return showToast('لطفا یک روش پرداخت انتخاب کنید.', 'error');

    setSubmitting(true);
    try {
      // 🎯 ۱. ایجاد فاکتور از سبد خرید
      const isWallet = selectedGateway === 'wallet';

      const invoiceRes = await apiFetch('/api/v1/financial/invoices/create_from_cart/', {
        method: 'POST',
        body: JSON.stringify({
          payment_method: isWallet ? 'wallet' : 'online_gateway', // ارسال متد پرداخت برای تشخیص بک‌اند
          notes: billingInfo.customer_notes,
          // ارسال اطلاعات هویتی و پستی در صورت پشتیبانی در سریالایزر بک‌اند
          billing_name: billingInfo.billing_name,
          billing_phone: billingInfo.billing_phone,
          billing_address: billingInfo.billing_address,
          billing_postal_code: billingInfo.billing_postal_code,
        })
      });

      const invoiceData = await invoiceRes.json();
      if (!invoiceRes.ok) throw new Error(invoiceData.error || 'خطا در صدور فاکتور نهایی.');

      // 🎯 ۲. هدایت هوشمند بر اساس نوع پرداخت
      if (isWallet) {
        // پرداخت کیف پول به صورت خودکار در متد create_from_cart انجام می‌شود
        showToast('سفارش شما با موفقیت ثبت و از کیف پول پرداخت شد!', 'success');
        router.push(`/profile/invoices/${invoiceData.invoice.id}`);
      }
      else {
        // 🎯 ۳. اتصال به درگاه‌های بانکی برای سایر روش‌ها
        const payRes = await apiFetch('/api/v1/payment/pay/', {
          method: 'POST',
          body: JSON.stringify({
            amount: cart.grand_total,
            invoice_id: invoiceData.invoice.id,
            gateway_id: selectedGateway,
            callback_url: `${window.location.origin}/payment/verify`
          })
        });

        const payData = await payRes.json();
        if (!payRes.ok) throw new Error(payData.error || 'خطا در تولید لینک پرداخت.');

        // انتقال به درگاه بانکی
        window.location.href = payData.payment_url;
      }

    } catch (error) {
      showToast(error.message, 'error');
      setSubmitting(false);
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', width: '100%' }}>آماده‌سازی فاکتور...</h2></PageWrapper>;

  return (
    <PageWrapper>
      <div>
        <Card>
          <SectionTitle>اطلاعات ارسال و صورت‌حساب</SectionTitle>
          <FormGrid id="checkout-form" onSubmit={handleCheckout}>
            <InputGroup>
              <Label>نام و نام خانوادگی تحویل گیرنده</Label>
              <Input required value={billingInfo.billing_name} onChange={(e) => setBillingInfo({...billingInfo, billing_name: e.target.value})} />
            </InputGroup>

            <InputGroup>
              <Label>شماره تماس (جهت هماهنگی ارسال)</Label>
              <Input required dir="ltr" value={billingInfo.billing_phone} onChange={(e) => setBillingInfo({...billingInfo, billing_phone: e.target.value})} />
            </InputGroup>

            <InputGroup fullWidth>
              <Label>آدرس دقیق پستی</Label>
              <TextArea required value={billingInfo.billing_address} onChange={(e) => setBillingInfo({...billingInfo, billing_address: e.target.value})} />
            </InputGroup>

            <InputGroup>
              <Label>کد پستی (۱۰ رقمی)</Label>
              <Input required dir="ltr" maxLength={10} value={billingInfo.billing_postal_code} onChange={(e) => setBillingInfo({...billingInfo, billing_postal_code: e.target.value})} />
            </InputGroup>

            <InputGroup fullWidth>
              <Label>یادداشت سفارش (اختیاری)</Label>
              <TextArea
                placeholder="اگر نکته‌ای برای بسته‌بندی یا ارسال دارید بنویسید..."
                value={billingInfo.customer_notes}
                onChange={(e) => setBillingInfo({...billingInfo, customer_notes: e.target.value})}
              />
            </InputGroup>
          </FormGrid>
        </Card>

        <Card>
          <SectionTitle>روش پرداخت</SectionTitle>
          <GatewayGrid>
            {gateways.map(gw => (
              <GatewayCard
                key={gw.id}
                selected={selectedGateway === gw.id}
                onClick={() => setSelectedGateway(gw.id)}
              >
                <span className="icon">{gw.type_display?.icon || '💳'}</span>
                <span className="name">{gw.name}</span>
              </GatewayCard>
            ))}
          </GatewayGrid>
        </Card>
      </div>

      <div>
        <Card style={{ position: 'sticky', top: '100px' }}>
          <SectionTitle>خلاصه نهایی فاکتور</SectionTitle>

          <SummaryRow>
            <span>مبلغ سفارش:</span>
            <span>{formatPrice(cart.subtotal)}</span>
          </SummaryRow>

          {cart.discount_percent > 0 && (
            <SummaryRow style={{ color: 'var(--success)' }}>
              <span>تخفیف:</span>
              <span>- {formatPrice(cart.discount_total)}</span>
            </SummaryRow>
          )}

          <div style={{ height: '1px', backgroundColor: 'var(--border)', margin: '1rem 0' }} />

          <SummaryRow highlight>
            <span>مبلغ قابل پرداخت:</span>
            <span style={{ color: 'var(--primary)' }}>{formatPrice(cart.grand_total)}</span>
          </SummaryRow>

          <PayButton type="submit" form="checkout-form" disabled={submitting}>
            {submitting ? 'در حال انتقال به درگاه...' : 'پرداخت و ثبت نهایی سفارش'}
          </PayButton>
        </Card>
      </div>
    </PageWrapper>
  );
}