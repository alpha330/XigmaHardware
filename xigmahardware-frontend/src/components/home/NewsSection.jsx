'use client';
import styled from '@emotion/styled';
import Link from 'next/link';
import { toJalali } from '@/lib/dateUtils';

const Section = styled.section`
  padding: 3rem 1rem;
  background: ${({ theme }) => theme.colors.surface};
`;

const Title = styled.h2`
  text-align: center;
  margin-bottom: 2rem;
  color: ${({ theme }) => theme.colors.text};
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
`;

const Card = styled.div`
  background: ${({ theme }) => theme.colors.background};
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.radius};
  box-shadow: ${({ theme }) => theme.shadows.sm};
`;

const Date = styled.span`
  font-size: 0.8rem;
  color: ${({ theme }) => theme.colors.textSecondary};
`;

export default function NewsSection({ news = [] }) {
  return (
    <Section>
      <Title>اخبار و مقالات</Title>
      <Grid>
        {news.slice(0, 6).map(item => (
          <Link key={item.id} href={`/news/${item.slug}`} passHref legacyBehavior>
            <Card as="a">
              <h3>{item.title}</h3>
              <p style={{ color: 'inherit' }}>{item.excerpt?.substring(0, 100)}...</p>
              <Date>{toJalali(item.published_at)}</Date>
            </Card>
          </Link>
        ))}
      </Grid>
    </Section>
  );
}