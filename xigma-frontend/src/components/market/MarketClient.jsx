// src/components/market/MarketClient.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import ProductCard from '../shared/ProductCard';

const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  gap: 2rem;
  align-items: flex-start;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const Sidebar = styled.aside`
  width: 280px;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  position: sticky;
  top: 100px; /* زیر هدر فیکس می‌شود */
  flex-shrink: 0;

  @media (max-width: 768px) {
    width: 100%;
    position: static;
  }
`;

const MainContent = styled.main`
  flex: 1;
  width: 100%;
`;

const FilterTitle = styled.h3`
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

const CategoryList = styled.ul`
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const CategoryItem = styled(Link)`
  display: block;
  padding: 0.5rem;
  color: ${({ theme, active }) => active ? theme.colors.primary : theme.colors.textMuted};
  font-weight: ${({ active }) => active ? 'bold' : 'normal'};
  border-radius: 8px;
  transition: all 0.2s ease;
  background-color: ${({ theme, active }) => active ? `${theme.colors.primary}15` : 'transparent'};

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
    background-color: ${({ theme }) => `${theme.colors.primary}10`};
  }
`;

const TopBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
`;

const ResultCount = styled.span`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.95rem;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.5rem;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 4rem 2rem;
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: 16px;
  border: 1px dashed ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMuted};
`;

export default function MarketClient({ products, categories }) {
  const searchParams = useSearchParams();
  const currentCategory = searchParams.get('category');

  return (
    <PageWrapper>
      {/* سایدبار فیلترها و دسته‌بندی‌ها */}
      <Sidebar>
        <FilterTitle>دسته‌بندی محصولات</FilterTitle>
        <CategoryList>
          {/* گزینه همه محصولات */}
          <li>
            <CategoryItem
              href="/market"
              active={!currentCategory}
            >
              همه محصولات
            </CategoryItem>
          </li>

          {/* لیست دسته‌بندی‌های سرور */}
          {Array.isArray(categories) && categories.map((cat) => (
            <li key={cat.id}>
              <CategoryItem
                href={`/market?category=${cat.id}`}
                active={currentCategory === String(cat.id)}
              >
                {cat.name || cat.title}
              </CategoryItem>
            </li>
          ))}
        </CategoryList>
      </Sidebar>

      {/* محتوای اصلی و لیست محصولات */}
      <MainContent>
        <TopBar>
          <h1 style={{ fontSize: '1.5rem', color: 'var(--textMain)' }}>فروشگاه سخت‌افزار</h1>
          <ResultCount>{products?.length || 0} کالا یافت شد</ResultCount>
        </TopBar>

        {products && products.length > 0 ? (
          <Grid>
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </Grid>
        ) : (
          <EmptyState>
            <h3>محصولی در این دسته‌بندی یافت نشد!</h3>
            <p style={{ marginTop: '1rem' }}>لطفاً فیلترهای خود را تغییر دهید یا به صفحه همه محصولات برگردید.</p>
          </EmptyState>
        )}
      </MainContent>
    </PageWrapper>
  );
}