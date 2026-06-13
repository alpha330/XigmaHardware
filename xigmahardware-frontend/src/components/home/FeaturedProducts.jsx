'use client';
import styled from '@emotion/styled';
import Link from 'next/link';
import { formatToman } from '@/lib/formatNumber';

const Section = styled.section`
  padding: 3rem 1rem;
`;

const Title = styled.h2`
  text-align: center;
  margin-bottom: 2rem;
  color: ${({ theme }) => theme.colors.text};
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
`;

const Card = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.radius};
  box-shadow: ${({ theme }) => theme.shadows.md};
  overflow: hidden;
  transition: transform 0.2s;
  &:hover { transform: translateY(-5px); }
`;

const Image = styled.img`
  width: 100%;
  height: 200px;
  object-fit: cover;
`;

const Info = styled.div`
  padding: 1rem;
`;

const Price = styled.div`
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
  margin-top: 0.5rem;
`;

export default function FeaturedProducts({ products = [] }) {
  return (
    <Section>
      <Title>محصولات ویژه</Title>
      <Grid>
        {products.slice(0, 8).map(product => (
          <Link key={product.id} href={`/products/${product.slug}`} passHref legacyBehavior>
            <Card as="a">
              <Image src={product.main_image || '/placeholder.jpg'} alt={product.title} />
              <Info>
                <h3>{product.title}</h3>
                <Price>{formatToman(product.final_price)}</Price>
              </Info>
            </Card>
          </Link>
        ))}
      </Grid>
    </Section>
  );
}