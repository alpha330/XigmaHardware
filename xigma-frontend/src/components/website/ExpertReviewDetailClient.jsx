// src/components/website/ExpertReviewDetailClient.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';

const PageWrapper = styled.div`
  max-width: 900px;
  margin: 0 auto;
  padding: 4rem 2rem;
`;

const Hero = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 3rem;
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  overflow: hidden;
`;

const Badge = styled.span`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  display: inline-block;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1.5rem;
  line-height: 1.4;
`;

const ScoreBox = styled.div`
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid ${({ theme }) => theme.colors.primary};
  margin: 0 auto;
`;

const ScoreNum = styled.span`
  font-size: 2rem;
  font-weight: 900;
  color: ${({ theme }) => theme.colors.primary};
`;

const ScoreLabel = styled.span`
  font-size: 0.8rem;
  color: ${({ theme }) => theme.colors.textMuted};
  text-transform: uppercase;
`;

const ProsConsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ListBox = styled.div`
  background-color: ${({ theme, type }) => type === 'pros' ? `${theme.colors.success}10` : `${theme.colors.error}10`};
  border: 1px solid ${({ theme, type }) => type === 'pros' ? theme.colors.success : theme.colors.error};
  border-radius: 12px;
  padding: 1.5rem;

  h3 {
    color: ${({ theme, type }) => type === 'pros' ? theme.colors.success : theme.colors.error};
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  ul {
    list-style: none;
    padding: 0;
  }

  li {
    color: ${({ theme }) => theme.colors.textMain};
    margin-bottom: 0.8rem;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;

    &::before {
      content: '${({ type }) => type === 'pros' ? '✓' : '✗'}';
      color: ${({ theme, type }) => type === 'pros' ? theme.colors.success : theme.colors.error};
      font-weight: bold;
    }
  }
`;

const ArticleBody = styled.div`
  color: ${({ theme }) => theme.colors.textMain};
  line-height: 2;
  font-size: 1.1rem;

  h2 {
    color: ${({ theme }) => theme.colors.primary};
    margin: 2.5rem 0 1rem;
  }

  p {
    color: ${({ theme }) => theme.colors.textMuted};
    margin-bottom: 1.5rem;
  }
`;

export default function ExpertReviewDetailClient({ review }) {
  if (!review) return null;

  return (
    <PageWrapper>
      <Hero>
        <Badge>تست و بررسی لابراتوار</Badge>
        <Title>{review.title}</Title>
        <ScoreBox>
          <ScoreNum>{review.expert_score || '9.0'}</ScoreNum>
          <ScoreLabel>امتیاز زیگما</ScoreLabel>
        </ScoreBox>
      </Hero>

      <ProsConsGrid>
        <ListBox type="pros">
          <h3>نقاط قوت</h3>
          <ul>
            {review.pros ? review.pros.map((pro, i) => <li key={i}>{pro}</li>) : (
              <>
                <li>کیفیت ساخت فوق‌العاده و پایداری بالا</li>
                <li>عملکرد خنک‌کننده در زیر بار سنگین</li>
                <li>ارزش خرید مناسب در برابر رقبا</li>
              </>
            )}
          </ul>
        </ListBox>
        <ListBox type="cons">
          <h3>نقاط ضعف</h3>
          <ul>
            {review.cons ? review.cons.map((con, i) => <li key={i}>{con}</li>) : (
              <>
                <li>نیاز به فضای زیاد در رک</li>
                <li>مصرف انرژی کمی بالاتر از نسل قبل</li>
              </>
            )}
          </ul>
        </ListBox>
      </ProsConsGrid>

      <ArticleBody dangerouslySetInnerHTML={{ __html: review.content || '<p>متن کامل بررسی به زودی قرار خواهد گرفت...</p>' }} />
    </PageWrapper>
  );
}