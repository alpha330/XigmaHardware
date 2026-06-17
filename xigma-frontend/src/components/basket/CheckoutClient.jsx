// src/components/basket/CheckoutClient.jsx
'use client';
import React, { useState, useEffect,useRef } from 'react';
import styled from '@emotion/styled';
import { useRouter } from 'next/navigation';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';
import PageLoader from  '@/components/shared/PageLoader'
import dynamic from 'next/dynamic';

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

// 🎯 آپدیت استایل درگاه برای پشتیبانی از حالت Disabled و Grayout
const GatewayCard = styled.div`
  border: 2px solid ${({ theme, selected, disabled }) =>
    disabled ? theme.colors.border : (selected ? theme.colors.primary : theme.colors.border)};
  background-color: ${({ theme, selected, disabled }) =>
    disabled ? theme.colors.background : (selected ? `${theme.colors.primary}10` : theme.colors.background)};
  padding: 1rem;
  border-radius: 12px;
  text-align: center;
  transition: all 0.2s;

  /* افکت‌های مربوط به غیرفعال بودن */
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  opacity: ${({ disabled }) => disabled ? 0.5 : 1};
  filter: ${({ disabled }) => disabled ? 'grayscale(100%)' : 'none'};

  ${({ disabled, theme }) => !disabled && `
    &:hover {
      border-color: ${theme.colors.primary};
    }
  `}

  .icon { font-size: 2rem; margin-bottom: 0.5rem; display: block; }
  .name { font-weight: bold; font-size: 0.95rem; color: ${({ theme }) => theme.colors.textMain}; }
  .error-text { font-size: 0.75rem; color: ${({ theme }) => theme.colors.error}; margin-top: 0.5rem; display: block; }
`;

const CouponBox = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed ${({ theme }) => theme.colors.border};

  input {
    flex: 1;
    background-color: ${({ theme }) => theme.colors.background};
    border: 1px solid ${({ theme }) => theme.colors.border};
    color: ${({ theme }) => theme.colors.textMain};
    padding: 0.8rem;
    border-radius: 8px;
    outline: none;
    text-transform: uppercase;
  }

  button {
    background-color: ${({ theme }) => theme.colors.secondary};
    color: white;
    border: none;
    padding: 0 1rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    &:disabled { opacity: 0.7; cursor: not-allowed; }
  }
`;

const AppliedCouponBadge = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: ${({ theme }) => `${theme.colors.success}15`};
  color: ${({ theme }) => theme.colors.success};
  padding: 0.8rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid ${({ theme }) => theme.colors.success};
  font-weight: bold;
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

const OrderTable = styled.div`
  margin-bottom: 1.5rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 8px;
  overflow: hidden;
`;

const OrderTableHeader = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr;
  background-color: ${({ theme }) => theme.colors.background};
  padding: 0.8rem;
  font-size: 0.85rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.textMuted};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

const OrderTableRow = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr;
  padding: 0.8rem;
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.textMain};
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  align-items: center;

  &:last-child {
    border-bottom: none;
  }

  .product-name {
    font-weight: bold;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-left: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .product-qty {
    text-align: center;
    color: ${({ theme }) => theme.colors.textMuted};
  }

  .product-price {
    text-align: left;
    font-weight: bold;
  }

  .discount-badge {
    font-size: 0.7rem;
    background-color: ${({ theme }) => theme.colors.error};
    color: #fff;
    padding: 0.1rem 0.4rem;
    border-radius: 12px;
  }
`;

const NeshanMap = dynamic(() => import('react-neshan-map-leaflet'), {
  ssr: false,
});

// ================= COMPONENT =================
export default function CheckoutClient() {
  const { showToast } = useToast();
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [coords, setCoords] = useState({ lat: 35.7, lng: 51.4 });
  // استیت‌های داده
  const [cart, setCart] = useState(null);
  const [gateways, setGateways] = useState([]);
  const [selectedGateway, setSelectedGateway] = useState(null);
  const [walletBalance, setWalletBalance] = useState(0); // 🎯 استیت جدید برای موجودی کیف پول

  // استیت‌های کوپن
  const [couponCode, setCouponCode] = useState('');
  const [couponLoading, setCouponLoading] = useState(false);
  const [appliedCoupon, setAppliedCoupon] = useState(null);

  const [billingInfo, setBillingInfo] = useState({
    billing_name: '',
    billing_phone: '',
    billing_postal_code: '',
    billing_address: '',
    customer_notes: ''
  });
  const mapRef = useRef(null);
  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price) + ' تومان';


  useEffect(() => {
    const loadLeafletStyles = async () => {
      await import('leaflet/dist/leaflet.css');
      await import('leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css');
      await import('leaflet-defaulticon-compatibility');
    };
    loadLeafletStyles();
    const fetchInitialData = async () => {
      try {
        const [cartRes, profileRes, userRes, gatewaysRes] = await Promise.all([
          apiFetch('/api/v1/basket/carts/my_cart/'),
          apiFetch('/api/v1/accounts/me/profile/'),
          apiFetch('/api/v1/accounts/me/'),
          apiFetch('/api/v1/payment/gateways/active_gateways/')
        ]);

        if (!cartRes.ok) return router.push('/basket/cart');

        const cartData = await cartRes.json();
        if (!cartData.can_checkout) {
          showToast('سبد خرید شما برای پرداخت آماده نیست.', 'error');
          return router.push('/basket/cart');
        }
        setCart(cartData);

        // پر کردن اطلاعات کاربر و استخراج موجودی کیف پول
        let name = '', phone = '', address = '', postal = '', balance = 0;
        if (userRes.ok) {
          const u = await userRes.json();
          name = `${u.first_name || ''} ${u.last_name || ''}`.trim();
          phone = u.mobile || '';
          // 🎯 دریافت موجودی (ممکن است در بک‌اند شما نام این فیلد wallet_balance یا balance باشد)
          balance = u.wallet_balance || u.balance || 0;
        }
        if (profileRes.ok) {
          const p = await profileRes.json();
          const profileData = p.profile || p;
          address = profileData.address || '';
          postal = profileData.postal_code || '';
          if (!balance) balance = profileData.wallet_balance || 0;
        }

        setWalletBalance(parseFloat(balance));
        setBillingInfo({ billing_name: name, billing_phone: phone, billing_address: address, billing_postal_code: postal, customer_notes: '' });

        if (gatewaysRes.ok) {
          const gwData = await gatewaysRes.json();
          const allGateways = [
            { id: 'wallet', name: 'کیف پول داخلی', type: 'wallet', type_display: { icon: '💰' } },
            ...gwData
          ];
          setGateways(allGateways);

          // 🎯 انتخاب هوشمند درگاه پیش‌فرض: اگر کیف پول پول نداشت، درگاه آنلاین را انتخاب کن
          if (balance < cartData.grand_total && gwData.length > 0) {
            setSelectedGateway(gwData[0].id); // اولین درگاه بانکی
          } else {
            setSelectedGateway(allGateways[0]?.id); // کیف پول
          }
        }

      } catch (error) {
        showToast('خطا در دریافت اطلاعات. لطفا صفحه را رفرش کنید.', 'error');
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [router, showToast]);


  const getAddressFromCoords = async (lat, lng) => {
    try {
      const response = await fetch(
        `https://api.neshan.org/v5/reverse?lat=${lat}&lng=${lng}`,
        { headers: { 'Api-Key':'service.7a95737616be44d98464a6eb06308184' } }
      );
      const data = await response.json();
      if (data.formatted_address) {
        setBillingInfo(prev => ({ ...prev, billing_address: data.formatted_address }));
      }
    } catch (error) {
      showToast('خطا در دریافت خودکار آدرس از نقشه', 'error');
    }
  };

  const handleApplyCoupon = async (e) => {
    e.preventDefault();
    if (!couponCode.trim()) return showToast('لطفاً کد تخفیف را وارد کنید.', 'warning');

    setCouponLoading(true);
    try {
      const res = await apiFetch(`/api/v1/financial/coupons/validate/?code=${couponCode}`);
      const data = await res.json();

      if (!res.ok || !data.valid) {
        throw new Error(data.message || 'کد تخفیف نامعتبر است.');
      }

      let discountAmount = 0;
      if (data.discount_type === 'percent') {
        discountAmount = cart.subtotal * (data.discount_value / 100);
      } else {
        discountAmount = Math.min(data.discount_value, cart.subtotal);
      }

      setAppliedCoupon({ code: couponCode, amount: discountAmount });
      showToast('کد تخفیف تایید شد و هنگام پرداخت اعمال می‌شود!', 'success');

    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setCouponLoading(false);
    }
  };

  const handleCheckout = async (e) => {
    e.preventDefault();
    if (!selectedGateway) return showToast('لطفا یک روش پرداخت انتخاب کنید.', 'error');

    setSubmitting(true);
    try {
      const invoiceRes = await apiFetch('/api/v1/financial/invoices/create_from_cart/', {
        method: 'POST',
        body: JSON.stringify({
          payment_method: 'online_gateway',
          notes: billingInfo.customer_notes
        })
      });
      const invData = await invoiceRes.json();
      if (!invoiceRes.ok) throw new Error(invData.error || 'خطا در ایجاد فاکتور.');
      const invoiceId = invData.invoice.id;

      await apiFetch(`/api/v1/financial/invoices/${invoiceId}/`, {
        method: 'PATCH',
        body: JSON.stringify({
          billing_name: billingInfo.billing_name,
          billing_phone: billingInfo.billing_phone,
          billing_address: billingInfo.billing_address,
          billing_postal_code: billingInfo.billing_postal_code,
        })
      });

      if (appliedCoupon) {
        await apiFetch('/api/v1/financial/coupons/apply/', {
          method: 'POST',
          body: JSON.stringify({ code: appliedCoupon.code, invoice_id: invoiceId })
        });
      }

      const payRes = await apiFetch('/api/v1/payment/pay/', {
        method: 'POST',
        body: JSON.stringify({
          amount: cart.grand_total - (appliedCoupon ? appliedCoupon.amount : 0),
          invoice_id: invoiceId,
          gateway_id: selectedGateway,
          callback_url: `${window.location.origin}/payment/verify`
        })
      });

      const payData = await payRes.json();
      if (!payRes.ok) throw new Error(payData.error || 'خطا در تولید لینک پرداخت.');

      if (selectedGateway === 'wallet') {
        showToast('پرداخت با کیف پول انجام شد.', 'success');
        router.push(`/profile/invoices/${invoiceId}`);
      } else {
        window.location.href = payData.payment_url;
      }

    } catch (error) {
      showToast(error.message, 'error');
      setSubmitting(false);
    }
  };

  if (loading || !cart) {
    return <PageLoader text="در حال آماده‌سازی فاکتور..." fullHeight={true} />;
  }
  const displayTotalDiscount = cart.discount_total + (appliedCoupon ? appliedCoupon.amount : 0);
  const displayTax = cart.tax_amount || 0;
  const displayGrandTotal = cart.grand_total - (appliedCoupon ? appliedCoupon.amount : 0);

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
            <InputGroup fullWidth>
              <Label>انتخاب موقعیت دقیق روی نقشه</Label>
              <div style={{ height: '300px', borderRadius: '8px', overflow: 'hidden' }}>
                {/* استفاده از شرط برای جلوگیری از رندر مجدد غیرضروری */}
                <NeshanMap
                  ref={mapRef}
                  mapKey="web.65dcd03c27774f60adbebfa70248785b"
                  defaultType="neshan"
                  center={coords}
                  zoom={14}
                  onChange={(e) => {
                    setCoords({ lat: e.lat, lng: e.lng });
                    getAddressFromCoords(e.lat, e.lng);
                  }}
                />
              </div>
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
            {gateways.map(gw => {
              // 🎯 محاسبه وضعیت قفل بودن برای کیف پول
              const isWallet = gw.id === 'wallet';
              const isInsufficient = isWallet && walletBalance < displayGrandTotal;

              return (
                <GatewayCard
                  key={gw.id}
                  selected={selectedGateway === gw.id}
                  disabled={isInsufficient}
                  onClick={() => {
                    // فقط اگر غیرفعال نبود اجازه کلیک بده
                    if (!isInsufficient) setSelectedGateway(gw.id);
                  }}
                  title={isInsufficient ? `موجودی شما (${formatPrice(walletBalance)}) کمتر از مبلغ فاکتور است` : ''}
                >
                  <span className="icon">{gw.type_display?.icon || '💳'}</span>
                  <span className="name">{gw.name}</span>
                  {/* 🎯 نمایش پیام خطای کوچک زیر کیف پول */}
                  {isInsufficient && <span className="error-text">موجودی ناکافی</span>}
                </GatewayCard>
              );
            })}
          </GatewayGrid>
        </Card>
      </div>

      <div>
        <Card style={{ position: 'sticky', top: '100px' }}>
          <SectionTitle>خلاصه نهایی فاکتور</SectionTitle>

          <OrderTable>
            <OrderTableHeader>
              <span>محصول</span>
              <span style={{ textAlign: 'center' }}>تعداد</span>
              <span style={{ textAlign: 'left' }}>قیمت نهایی</span>
            </OrderTableHeader>
            {cart.items.map(item => (
              <OrderTableRow key={item.id}>
                <div className="product-name" title={item.product_name}>
                  {item.product_name}
                  {item.discount_percent > 0 && (
                    <span className="discount-badge">%{item.discount_percent}</span>
                  )}
                </div>
                <div className="product-qty">{item.quantity} عدد</div>
                <div className="product-price">{formatPrice(item.total_price)}</div>
              </OrderTableRow>
            ))}
          </OrderTable>

          {!appliedCoupon ? (
            <CouponBox>
              <input
                type="text"
                placeholder="کد تخفیف خود را وارد کنید"
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
              />
              <button
                type="button"
                onClick={handleApplyCoupon}
                disabled={couponLoading || !couponCode}
              >
                {couponLoading ? '...' : 'اعمال'}
              </button>
            </CouponBox>
          ) : (
             <AppliedCouponBadge>
               <span>کد {appliedCoupon.code} فعال است</span>
               <span>تخفیف: {formatPrice(appliedCoupon.amount)}</span>
             </AppliedCouponBadge>
          )}

          <SummaryRow>
            <span>تعداد کل کالاها:</span>
            <span>{cart.total_quantity} عدد</span>
          </SummaryRow>

          <SummaryRow>
            <span>مبلغ سفارش:</span>
            <span>{formatPrice(cart.subtotal)}</span>
          </SummaryRow>

          {displayTotalDiscount > 0 && (
            <SummaryRow style={{ color: 'var(--success)' }}>
              <span>مجموع تخفیف‌ها:</span>
              <span>- {formatPrice(displayTotalDiscount)}</span>
            </SummaryRow>
          )}

          {displayTax > 0 && (
            <SummaryRow>
              <span>مالیات بر ارزش افزوده:</span>
              <span>+ {formatPrice(displayTax)}</span>
            </SummaryRow>
          )}

          <div style={{ height: '1px', backgroundColor: 'var(--border)', margin: '1rem 0' }} />

          <SummaryRow highlight>
            <span>مبلغ قابل پرداخت:</span>
            <span style={{ color: 'var(--primary)' }}>{formatPrice(displayGrandTotal)}</span>
          </SummaryRow>

          <PayButton type="submit" form="checkout-form" disabled={submitting}>
            {submitting ? 'در حال پردازش...' : 'پرداخت و ثبت نهایی سفارش'}
          </PayButton>
        </Card>
      </div>
    </PageWrapper>
  );
}