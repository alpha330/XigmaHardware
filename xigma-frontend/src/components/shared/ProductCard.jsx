// src/components/shared/ProductCard.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';

const Card = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 86, 210, 0.1); /* سایه ملایم آبی */
    border-color: ${({ theme }) => theme.colors.primary};
  }
`;

const ImagePlaceholder = styled.div`
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.background} 0%, ${({ theme }) => theme.colors.border} 100%);
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Title = styled.h3`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
  line-height: 1.5;
`;

const PriceWrapper = styled.div`
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
`;

const Price = styled.span`
  font-size: 1.25rem;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
`;

const AddToCartBtn = styled.button`
  background-color: transparent;
  border: 2px solid ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.primary};
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.primary};
    color: #fff;
  }
`;

export default function ProductCard({ product }) {
  // فرمت کردن قیمت به تومان
  const formattedPrice = new Intl.NumberFormat('fa-IR').format(product.market_price || 0);

  return (
    <Card>
      <Link href={`/market/products/${product.id}`}>
        <ImagePlaceholder>عکس محصول</ImagePlaceholder>
        <Title>{product.name || 'محصول ناشناس'}</Title>
      </Link>
      <PriceWrapper>
        <Price>{formattedPrice} تومان</Price>
        <AddToCartBtn title="افزودن به سبد خرید">+</AddToCartBtn>
      </PriceWrapper>
    </Card>
  );
}