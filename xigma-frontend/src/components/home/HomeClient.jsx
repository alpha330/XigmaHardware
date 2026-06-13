// src/components/home/HomeClient.jsx
'use client';

import styled from '@emotion/styled';
import Hero from './Hero';
import ProductCard from '../shared/ProductCard';
import ArticleCard from '../shared/ArticleCard';
import ReviewCard from '../shared/ReviewCard';

// این استایل داینامیک باعث میشه تم به درستی روی کل سکشن اعمال بشه
const SectionWrapper = styled.section`
  padding: 4rem 2rem;
  background-color: ${({ bgType, theme }) =>
    bgType === 'surface' ? theme.colors.surface : theme.colors.background};
  transition: background-color 0.3s ease;
  width: 100%;
`;

const SectionContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const SectionTitle = styled.h2`
  font-size: 2rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 2.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: color 0.3s ease;

  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: ${({ theme }) => theme.colors.border};
    transition: background-color 0.3s ease;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 2rem;
`;

export default function HomeClient({ featuredProducts, bestsellers, articles, reviews }) {
  return (
    <>
      <Hero />

      {/* محصولات ویژه - بک گراند اصلی */}
      <SectionWrapper bgType="background">
        <SectionContainer>
          <SectionTitle>🔥 محصولات ویژه</SectionTitle>
          <Grid>
            {featuredProducts?.map((product) => (
              <ProductCard key={`featured-${product.id}`} product={product} />
            ))}
          </Grid>
        </SectionContainer>
      </SectionWrapper>

      {/* پرفروش‌ترین‌ها - بک گراند Surface (مشکل تم اینجا حل شد) */}
      <SectionWrapper bgType="surface">
        <SectionContainer>
          <SectionTitle>⚡ پرفروش‌ترین‌ها</SectionTitle>
          <Grid>
            {bestsellers?.map((product) => (
              <ProductCard key={`bestseller-${product.id}`} product={product} />
            ))}
          </Grid>
        </SectionContainer>
      </SectionWrapper>

      {/* آخرین اخبار و مقالات */}
      <SectionWrapper bgType="background">
        <SectionContainer>
          <SectionTitle>📰 اخبار و مقالات دنیای سخت‌افزار</SectionTitle>
          <Grid>
            {articles?.map((article) => (
              <ArticleCard key={`article-${article.id}`} article={article} />
            ))}
          </Grid>
        </SectionContainer>
      </SectionWrapper>

      {/* نظرات کاربران */}
      <SectionWrapper bgType="surface">
        <SectionContainer>
          <SectionTitle>💬 نظرات مشتریان ما</SectionTitle>
          <Grid>
            {reviews?.map((review) => (
              <ReviewCard key={`review-${review.id}`} review={review} />
            ))}
          </Grid>
        </SectionContainer>
      </SectionWrapper>
    </>
  );
}