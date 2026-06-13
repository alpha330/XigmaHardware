'use client';
import styled from '@emotion/styled';
import Link from 'next/link';

const Hero = styled.section`
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary}, #1e3a8a);
  color: white;
  padding: 4rem 1rem;
  text-align: center;
  border-radius: 0 0 2rem 2rem;
  margin-bottom: 2rem;
`;

export default function HeroSection() {
  return (
    <Hero>
      <h1 style={{ fontSize: '2.5rem' }}>XigmaHardware</h1>
      <p style={{ fontSize: '1.2rem', margin: '1rem 0' }}>
        قدرت سخت‌افزار، اعتماد شما
      </p>
      <Link href="/products" passHref>
        <button style={{
          padding: '0.8rem 2rem',
          background: 'white',
          color: '#1a56db',
          border: 'none',
          borderRadius: '2rem',
          fontWeight: 'bold',
          cursor: 'pointer',
        }}>
          مشاهده محصولات
        </button>
      </Link>
    </Hero>
  );
}