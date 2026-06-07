// src/app/page.js
'use client';

import styled from '@emotion/styled';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { HeroSlider } from '@/components/home/HeroSlider';
import { ProductSection } from '@/components/home/ProductSection';

const Main = styled.main`
  min-height: 100vh;
`;

const Section = styled.section`
  max-width: 1400px;
  margin: 60px auto;
  padding: 0 24px;
`;

const SectionTitle = styled.h2`
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 32px;
  color: ${props => props.theme.colors.text.primary};
  position: relative;
  padding-right: 16px;

  &::before {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 32px;
    background: ${props => props.theme.colors.primary[500]};
    border-radius: 2px;
  }
`;

const ReviewGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
`;

const ReviewCard = styled.div`
  background: ${props => props.theme.colors.card};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: 24px;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const ReviewerInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`;

const Avatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: ${props => props.theme.colors.primary[100]};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: ${props => props.theme.colors.primary[700]};
`;

const NewsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
`;

const NewsCard = styled.div`
  background: ${props => props.theme.colors.card};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${props => props.theme.shadows.lg};
  }
`;

const NewsImage = styled.div`
  height: 180px;
  background: linear-gradient(135deg,
    ${props => props.theme.colors.primary[500]},
    ${props => props.theme.colors.primary[700]}
  );
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
`;

const NewsContent = styled.div`
  padding: 20px;
`;

const NewsTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: ${props => props.theme.colors.text.primary};
`;

const NewsDate = styled.span`
  font-size: 0.8rem;
  color: ${props => props.theme.colors.text.muted};
`;

// Mock Reviews
const reviews = [
  { id: 1, name: 'علی رضایی', initial: 'ع', product: 'سرور HP DL380 G10', rating: 5, text: 'عالی بود. پردازش فوق‌العاده سریع و گارانتی معتبر. حتماً پیشنهاد می‌کنم.' },
  { id: 2, name: 'مریم محمدی', initial: 'م', product: 'Dell PowerEdge R740', rating: 4, text: 'محصول خوبی بود. فقط ای کاش زودتر به دستم می‌رسید.' },
  { id: 3, name: 'شرکت فناوران', initial: 'ف', product: 'Cisco Switch C9300', rating: 5, text: 'برای سازمان ما خریداری شد. کیفیت بی‌نظیر و راه‌اندازی آسان.' },
];

// Mock News
const news = [
  { id: 1, title: 'ورود سری جدید سرورهای HP G11', date: '۱۵ خرداد ۱۴۰۵', emoji: '🆕' },
  { id: 2, title: 'تخفیف ویژه پایان سال - تا ۴۰٪', date: '۱۰ خرداد ۱۴۰۵', emoji: '🎉' },
  { id: 3, title: 'همکاری با Dell به عنوان نماینده رسمی', date: '۵ خرداد ۱۴۰۵', emoji: '🤝' },
];

export default function HomePage() {
  return (
    <>
      <Header />
      <Main>
        <HeroSlider />

        <ProductSection title="🔥 پرفروش‌ترین محصولات" />

        <Section>
          <SectionTitle>⭐ آخرین نظرات کاربران</SectionTitle>
          <ReviewGrid>
            {reviews.map(review => (
              <ReviewCard key={review.id}>
                <ReviewerInfo>
                  <Avatar>{review.initial}</Avatar>
                  <div>
                    <strong>{review.name}</strong>
                    <div style={{ fontSize: '0.85rem', color: '#888' }}>
                      {review.product}
                    </div>
                  </div>
                </ReviewerInfo>
                <div style={{ color: '#f59e0b', marginBottom: 8 }}>
                  {'⭐'.repeat(review.rating)}
                </div>
                <p style={{ color: '#666', fontSize: '0.9rem' }}>{review.text}</p>
              </ReviewCard>
            ))}
          </ReviewGrid>
        </Section>

        <ProductSection title="🆕 جدیدترین محصولات" />

        <Section>
          <SectionTitle>📰 اخبار و اطلاعیه‌ها</SectionTitle>
          <NewsGrid>
            {news.map(item => (
              <NewsCard key={item.id}>
                <NewsImage>{item.emoji}</NewsImage>
                <NewsContent>
                  <NewsTitle>{item.title}</NewsTitle>
                  <NewsDate>{item.date}</NewsDate>
                </NewsContent>
              </NewsCard>
            ))}
          </NewsGrid>
        </Section>
      </Main>
      <Footer />
    </>
  );
}