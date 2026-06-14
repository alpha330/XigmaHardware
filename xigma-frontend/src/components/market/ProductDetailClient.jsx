// src/components/market/ProductDetailClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';
import ProductReviews from './ProductReviews';

// ================= STYLES =================
const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
`;

const TopSection = styled.div`
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 3rem;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

// --- Gallery Styles ---
const GalleryArea = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const MainImage = styled.div`
  width: 100%;
  aspect-ratio: 1 / 1;
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
`;

const ThumbnailsList = styled.div`
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;

  &::-webkit-scrollbar { height: 6px; }
`;

const Thumbnail = styled.div`
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border: 2px solid ${({ theme, active }) => active ? theme.colors.primary : theme.colors.border};
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background-color: ${({ theme }) => theme.colors.background};

  img { width: 100%; height: 100%; object-fit: cover; }
`;

// --- Info Styles ---
const InfoArea = styled.div`
  display: flex;
  flex-direction: column;
`;

const Title = styled.h1`
  font-size: 1.8rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
  line-height: 1.4;
`;

const MetaRow = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

const RatingBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: #fbbf24;
  font-weight: bold;
`;

const ShortDesc = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  line-height: 1.8;
  margin-bottom: 2rem;
  font-size: 0.95rem;
`;

// --- Pricing & Action Styles ---
const ActionBox = styled.div`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: auto;
`;

const PriceRow = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
`;

const OldPrice = styled.div`
  color: ${({ theme }) => theme.colors.textMuted};
  text-decoration: line-through;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const DiscountBadge = styled.span`
  background-color: ${({ theme }) => theme.colors.error};
  color: #fff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  text-decoration: none;
`;

const FinalPrice = styled.div`
  color: ${({ theme }) => theme.colors.textMain};
  font-size: 1.8rem;
  font-weight: bold;

  span { font-size: 1rem; font-weight: normal; margin-right: 0.3rem; color: ${({ theme }) => theme.colors.textMuted}; }
`;

const CartControls = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;

  @media (max-width: 600px) { flex-direction: column; }
`;

const QuantitySelector = styled.div`
  display: flex;
  align-items: center;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 8px;
  overflow: hidden;

  button {
    background: none; border: none; width: 40px; height: 45px;
    font-size: 1.2rem; cursor: pointer; color: ${({ theme }) => theme.colors.textMain};
    &:hover { background-color: ${({ theme }) => theme.colors.border}; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }

  span { width: 40px; text-align: center; font-weight: bold; color: ${({ theme }) => theme.colors.textMain}; }
`;

const AddToCartBtn = styled.button`
  flex: 1;
  background-color: ${({ theme, outOfStock }) => outOfStock ? theme.colors.border : theme.colors.primary};
  color: ${({ theme, outOfStock }) => outOfStock ? theme.colors.textMuted : '#fff'};
  border: none;
  border-radius: 8px;
  padding: 0 2rem;
  height: 45px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: ${({ outOfStock }) => outOfStock ? 'not-allowed' : 'pointer'};
  transition: all 0.2s;
  width: 100%;

  &:hover:not(:disabled) {
    background-color: ${({ theme, outOfStock }) => outOfStock ? theme.colors.border : theme.colors.secondary};
  }
`;

// --- Bottom Tabs Styles ---
const TabsContainer = styled.div`
  margin-top: 3rem;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  overflow: hidden;
`;

const TabHeaders = styled.div`
  display: flex;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  background-color: ${({ theme }) => theme.colors.background};
`;

const Tab = styled.button`
  flex: 1;
  padding: 1.2rem;
  background: none;
  border: none;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  color: ${({ theme, active }) => active ? theme.colors.primary : theme.colors.textMuted};
  border-bottom: 3px solid ${({ theme, active }) => active ? theme.colors.primary : 'transparent'};
  transition: all 0.2s;

  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

const TabContent = styled.div`
  padding: 2rem;
  color: ${({ theme }) => theme.colors.textMain};
  line-height: 1.8;
  min-height: 300px;
`;

const SpecRow = styled.div`
  display: flex;
  padding: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};

  &:nth-of-type(even) { background-color: ${({ theme }) => theme.colors.background}; }
  &:last-child { border-bottom: none; }

  .key { flex: 1; font-weight: bold; color: ${({ theme }) => theme.colors.textMuted}; }
  .value { flex: 2; color: ${({ theme }) => theme.colors.textMain}; }
`;

export default function ProductDetailClient({ identifier }) {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [product, setProduct] = useState(null);

  const [selectedImage, setSelectedImage] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [actionLoading, setActionLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('desc'); // desc, specs, reviews

  const formatPrice = (price) => new Intl.NumberFormat('fa-IR').format(price);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await apiFetch(`/api/v1/market/products/${identifier}/`);
        if (res.ok) {
          const data = await res.json();
          setProduct(data);
          // تنظیم تصویر پیش‌فرض (اولین عکس گالری)
          if (data.media && data.media.length > 0) {
            setSelectedImage(data.media[0].image);
          }
        } else {
          showToast('محصول مورد نظر یافت نشد.', 'error');
        }
      } catch (error) {
        showToast('خطا در ارتباط با سرور.', 'error');
      } finally {
        setLoading(false);
      }
    };

    if (identifier) fetchProduct();
  }, [identifier, showToast]);

  const handleAddToCart = async () => {
    if (!product || product.available_quantity < 1) return;
    setActionLoading(true);

    try {
      const res = await apiFetch('/api/v1/basket/carts/add-item/', {
        method: 'POST',
        body: JSON.stringify({ product_id: product.id, quantity })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'خطا در افزودن به سبد خرید.');
      }

      showToast(`${product.title} به سبد خرید اضافه شد.`, 'success');
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <PageWrapper><h2 style={{ textAlign: 'center', padding: '5rem' }}>در حال بارگذاری محصول...</h2></PageWrapper>;
  if (!product) return <PageWrapper><h2 style={{ textAlign: 'center' }}>محصولی یافت نشد.</h2></PageWrapper>;

  const outOfStock = product.available_quantity < 1;

  // اطلاعات فنی استخراج شده از stock_product
  const specs = product.stock_info || {};

  return (
    <PageWrapper>
      <TopSection>
        {/* Gallery */}
        <GalleryArea>
          <MainImage>
            {selectedImage ? (
              <img src={selectedImage} alt={product.title} />
            ) : (
              <span style={{ fontSize: '4rem', opacity: 0.2 }}>📷</span>
            )}
          </MainImage>

          {product.media && product.media.length > 0 && (
            <ThumbnailsList>
              {product.media.map((med, idx) => (
                <Thumbnail
                  key={idx}
                  active={selectedImage === med.image}
                  onClick={() => setSelectedImage(med.image)}
                >
                  <img src={med.image} alt="thumbnail" />
                </Thumbnail>
              ))}
            </ThumbnailsList>
          )}
        </GalleryArea>

        {/* Info */}
        <InfoArea>
          <Title>{product.title}</Title>
          <MetaRow>
            <span>دسته: {specs.category || 'عمومی'}</span>
            <span>برند: {specs.brand || 'متفرقه'}</span>
            <RatingBadge>⭐ {product.avg_rating || 5.0} ({product.rating_count || 0} نظر)</RatingBadge>
          </MetaRow>

          <ShortDesc>
            {product.short_description || 'توضیح کوتاهی برای این محصول ثبت نشده است. لطفاً بخش توضیحات کامل را مطالعه کنید.'}
          </ShortDesc>

          <ActionBox>
            <PriceRow>
              {product.has_discount && (
                <OldPrice>
                  {formatPrice(product.market_price)}
                  <DiscountBadge>{product.discount_percent}% تخفیف</DiscountBadge>
                </OldPrice>
              )}
              <FinalPrice>
                {formatPrice(product.final_price || product.market_price)} <span>تومان</span>
              </FinalPrice>
            </PriceRow>

            <CartControls>
              <QuantitySelector>
                <button
                  onClick={() => setQuantity(q => Math.max(1, q - 1))}
                  disabled={outOfStock || quantity <= 1}
                >-</button>
                <span>{quantity}</span>
                <button
                  onClick={() => setQuantity(q => Math.min(product.available_quantity, product.max_order_quantity, q + 1))}
                  disabled={outOfStock || quantity >= product.available_quantity || quantity >= product.max_order_quantity}
                >+</button>
              </QuantitySelector>

              <AddToCartBtn
                onClick={handleAddToCart}
                disabled={outOfStock || actionLoading}
                outOfStock={outOfStock}
              >
                {outOfStock ? 'ناموجود در انبار' : (actionLoading ? 'در حال افزودن...' : 'افزودن به سبد خرید')}
              </AddToCartBtn>
            </CartControls>
          </ActionBox>
        </InfoArea>
      </TopSection>

      {/* Tabs */}
      <TabsContainer>
        <TabHeaders>
          <Tab active={activeTab === 'desc'} onClick={() => setActiveTab('desc')}>معرفی و توضیحات</Tab>
          <Tab active={activeTab === 'specs'} onClick={() => setActiveTab('specs')}>مشخصات فنی</Tab>
          <Tab active={activeTab === 'reviews'} onClick={() => setActiveTab('reviews')}>نظرات کاربران ({product.rating_count || 0})</Tab>
        </TabHeaders>

        <TabContent>
          {activeTab === 'desc' && (
            <div dangerouslySetInnerHTML={{ __html: product.full_description?.replace(/\n/g, '<br />') || 'توضیحات تکمیلی ثبت نشده است.' }} />
          )}

          {activeTab === 'specs' && (
            <div>
              {Object.keys(specs).length > 0 ? (
                <>
                  <SpecRow><span className="key">کد کالا (SKU)</span><span className="value">{specs.sku || '-'}</span></SpecRow>
                  <SpecRow><span className="key">وضعیت فیزیکی</span><span className="value">{specs.condition || '-'}</span></SpecRow>
                  <SpecRow><span className="key">برند</span><span className="value">{specs.brand || '-'}</span></SpecRow>
                  <SpecRow><span className="key">پردازنده (Processor)</span><span className="value">{specs.processor || '-'}</span></SpecRow>
                  <SpecRow><span className="key">حافظه رم (RAM)</span><span className="value">{specs.ram || '-'}</span></SpecRow>
                  <SpecRow><span className="key">فضای ذخیره‌سازی</span><span className="value">{specs.storage || '-'}</span></SpecRow>
                  <SpecRow><span className="key">فرم فاکتور</span><span className="value">{specs.form_factor || '-'}</span></SpecRow>
                </>
              ) : (
                <p>مشخصات فنی برای این کالا ثبت نشده است.</p>
              )}
            </div>
          )}

          {activeTab === 'reviews' && (
            <div>
              <ProductReviews productId={product.id} stats={product} />
            </div>
          )}
        </TabContent>
      </TabsContainer>

    </PageWrapper>
  );
}