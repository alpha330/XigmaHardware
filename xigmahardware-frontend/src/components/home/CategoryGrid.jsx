'use client';
import styled from '@emotion/styled';
import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faServer, faDesktop, faHome, faLaptop } from '@fortawesome/free-solid-svg-icons';

const iconsMap = { datacenter: faServer, office: faDesktop, home: faHome, workstation: faLaptop };

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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
`;

const Card = styled.div`
  background: ${({ theme }) => theme.colors.background};
  padding: 2rem;
  border-radius: ${({ theme }) => theme.radius};
  text-align: center;
  box-shadow: ${({ theme }) => theme.shadows.md};
  transition: transform 0.2s;
  &:hover { transform: translateY(-4px); }
`;

export default function CategoryGrid({ categories = [] }) {
  return (
    <Section>
      <Title>دسته‌بندی محصولات</Title>
      <Grid>
        {categories.map(cat => (
          <Link key={cat.id} href={`/categories/${cat.slug}`} passHref legacyBehavior>
            <Card as="a">
              <FontAwesomeIcon icon={iconsMap[cat.slug] || faServer} size="2x" color="#1a56db" />
              <h3 style={{ marginTop: '1rem' }}>{cat.name}</h3>
            </Card>
          </Link>
        ))}
      </Grid>
    </Section>
  );
}