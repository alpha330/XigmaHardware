// src/components/market/ProductDetailClient.jsx
'use client';

import React, { useState } from 'react';
import styled from '@emotion/styled';
import ReviewCard from '../shared/ReviewCard';

const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const ProductGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ImageGallery = styled.div`
  width: 100%;
  aspect-ratio: 1 / 1;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.background} 0%, ${({ theme }) => theme.colors.border} 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 1.2rem;
`;

const InfoSection = styled.div`
  display: flex;
  flex-direction: column;
`;

const Title = styled.h1`
  font-size: 2rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;
`;

const BrandCategory = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.9rem;

  span {
    background-color: ${({ theme }) => theme.colors.background};
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    border: 1px solid ${({ theme }) => theme.colors.border};
  }
`;

const PriceBox = styled.div`
  margin-top: auto;
  padding-top: 2rem;
  border-top: 1px dashed ${({ theme }) => theme.colors.border};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Price = styled.div`
  font-size: 1.8rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
`;

const AddToCartBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &:hover {
    background-color: ${({ theme }) => theme.colors.secondary};
    transform: translateY(-2px);
  }

  &:disabled {
    background-color: ${({ theme }) => theme.colors.border};
    cursor: not-allowed;
    transform: none;
  }
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;

  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: ${({ theme }) => theme.colors.border};
  }
`;

const SpecsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 3rem;
`;

const SpecItem = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 8px;

  span:first-of-type {
    color: ${({ theme }) => theme.colors.textMuted};
  }

  span:last-of-type {
    color: ${({ theme }) => theme.colors.textMain};
    font-weight: bold;
  }
`;

const ReviewsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
`;

export default function ProductDetailClient({ product, reviews }) {
  const [isAdding, setIsAdding] = useState(false);

  // تابع افزودن به سبد خرید
  const handleAddToCart = async () => {
    setIsAdding(true);
    try {
      const token = localStorage.getItem('token'); // دریافت توکن در صورت لاگین بودن کاربر

      const res = await fetch('http://localhost:8000/api/v1/basket/carts/add_item/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          product_id: product.id,
          quantity: 1,
          cart_type: 'cart'
        })
      });

      if (!res.ok) throw new Error('خطا در افزودن به سبد خرید');

      alert('محصول با موفقیت به سبد خرید اضافه شد!');
    } catch (error) {
      console.error(error);
      alert('درخواست با خطا مواجه شد. (شاید لاگین نیستید یا بک‌اند در دسترس نیست)');
    } finally {
      setIsAdding(false);
    }
  };

  if (!product) return <PageWrapper>محصول یافت نشد!</PageWrapper>;

  const formattedPrice = new Intl.NumberFormat('fa-IR').format(product.market_price || 0);

  return (
    <PageWrapper>
      <ProductGrid>
        <ImageGallery>تصویر محصول ({product.name})</ImageGallery>

        <InfoSection>
          <Title>{product.name}</Title>
          <BrandCategory>
            <span>دسته‌بندی: {product.category || 'نامشخص'}</span>
            <span>برند: {product.brand || 'نامشخص'}</span>
          </BrandCategory>

          <p style={{ color: 'var(--textMuted)', lineHeight: '1.8' }}>
            {product.description || 'توضیحات کاملی برای این محصول سخت‌افزاری در دسترس نیست. این کالا با گارانتی معتبر شرکتی عرضه می‌شود.'}
          </p>

          <PriceBox>
            <Price>{formattedPrice} تومان</Price>
            <AddToCartBtn onClick={handleAddToCart} disabled={isAdding}>
              {isAdding ? 'در حال افزودن...' : '🛒 افزودن به سبد خرید'}
            </AddToCartBtn>
          </PriceBox>
        </InfoSection>
      </ProductGrid>

      {/* بخش مشخصات فنی */}
      <SectionTitle>مشخصات فنی</SectionTitle>
      <SpecsGrid>
        <SpecItem>
          <span>وضعیت</span>
          <span>{product.condition === 'new' ? 'آکبند' : 'استوک'}</span>
        </SpecItem>
        {product.processor && (
          <SpecItem>
            <span>پردازنده</span>
            <span dir="ltr">{product.processor}</span>
          </SpecItem>
        )}
        {product.ram && (
          <SpecItem>
            <span>حافظه RAM</span>
            <span dir="ltr">{product.ram}</span>
          </SpecItem>
        )}
        {product.storage && (
          <SpecItem>
            <span>فضای ذخیره‌سازی</span>
            <span dir="ltr">{product.storage}</span>
          </SpecItem>
        )}
      </SpecsGrid>

      {/* بخش نظرات */}
      <SectionTitle>نظرات خریداران</SectionTitle>
      {reviews && reviews.length > 0 ? (
        <ReviewsGrid>
          {reviews.map((review) => (
            <ReviewCard key={review.id} review={review} />
          ))}
        </ReviewsGrid>
      ) : (
        <p style={{ color: 'var(--textMuted)' }}>هنوز نظری برای این محصول ثبت نشده است. شما اولین نفر باشید!</p>
      )}
    </PageWrapper>
  );
}