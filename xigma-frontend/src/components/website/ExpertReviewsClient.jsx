// src/components/website/ExpertReviewsClient.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';
import ExpertReviewCard from '../shared/ExpertReviewCard';

const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
`;

const HeaderSection = styled.div`
  text-align: center;
  margin-bottom: 4rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 900;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2.5rem;
`;

export default function ExpertReviewsClient({ reviews }) {
  return (
    <PageWrapper>
      <HeaderSection>
        <Title>لابراتوار تخصصی XigmaHardware</Title>
        <p style={{ color: 'var(--textMuted)', fontSize: '1.1rem' }}>
          بررسی موشکافانه، بنچمارک‌ها و تست‌های زیر بار تجهیزات سازمانی و قطعات توسط تیم فنی ما.
        </p>
      </HeaderSection>

      <Grid>
        {reviews?.map((review) => (
          <ExpertReviewCard key={review.id} review={review} />
        ))}
      </Grid>
    </PageWrapper>
  );
}