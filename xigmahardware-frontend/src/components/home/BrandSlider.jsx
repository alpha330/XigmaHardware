'use client';
import styled from '@emotion/styled';
import Link from 'next/link';

const Section = styled.section`
  padding: 3rem 1rem;
  text-align: center;
`;

const Title = styled.h2`
  margin-bottom: 2rem;
  color: ${({ theme }) => theme.colors.text};
`;

const Slider = styled.div`
  display: flex;
  gap: 2rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding: 1rem;
  &::-webkit-scrollbar { height: 4px; }
`;

const BrandCard = styled.div`
  scroll-snap-align: start;
  flex: 0 0 150px;
  padding: 1.5rem;
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radius};
  box-shadow: ${({ theme }) => theme.shadows.sm};
  text-align: center;
  transition: transform 0.2s;
  &:hover { transform: translateY(-4px); }
`;

export default function BrandSlider({ brands = [] }) {
  return (
    <Section>
      <Title>برندهای برتر</Title>
      <Slider>
        {brands.slice(0, 10).map(brand => (
          <Link key={brand.id} href={`/brands/${brand.slug}`} passHref legacyBehavior>
            <BrandCard as="a">
              {brand.logo ? (
                <img src={brand.logo} alt={brand.name} style={{ maxWidth: '100%', height: 'auto' }} />
              ) : (
                <h3>{brand.persian_name || brand.name}</h3>
              )}
            </BrandCard>
          </Link>
        ))}
      </Slider>
    </Section>
  );
}